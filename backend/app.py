# backend/app.py

import os
import re
import math
import logging
from collections import OrderedDict

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from dotenv import load_dotenv

import openai
import pandas as pd
import pandasql as psql

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure Flask-Caching
app.config['CACHE_TYPE'] = 'SimpleCache'  # Simple in-memory cache
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache timeout in seconds
cache = Cache(app)

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    exit(1)
openai.api_key = OPENAI_API_KEY

# Load and preprocess Zillow data
def load_zillow_data(file_path='data/Zillow_Data.csv') -> pd.DataFrame:
    try:
        if not os.path.exists(file_path):
            logger.error(f"Zillow data CSV file not found at path: {file_path}")
            return pd.DataFrame()
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()

        # Drop 'crawl_url_result' if present
        if 'crawl_url_result' in df.columns:
            df = df.drop(columns=['crawl_url_result'])

        # Convert 'price' to numeric
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', ''), errors='coerce')
        else:
            logger.warning("'price' column not found in Zillow data.")

        # Convert 'beds' and 'baths' to numeric
        for col in ['beds', 'baths']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                logger.warning(f"'{col}' column not found in Zillow data.")

        # Standardize 'city' and 'state'
        for col in ['city', 'state']:
            if col in df.columns:
                if col == 'city':
                    df[col] = df[col].str.title()
                elif col == 'state':
                    df[col] = df[col].str.upper()
            else:
                logger.warning(f"'{col}' column not found in Zillow data.")

        # Ensure 'zip_code' is string
        if 'zip_code' in df.columns:
            df['zip_code'] = df['zip_code'].astype(str)
        else:
            logger.warning("'zip_code' column not found in Zillow data.")

        return df
    except Exception as e:
        logger.error(f"Error loading Zillow data: {e}")
        return pd.DataFrame()

# Load and preprocess Broker data
def load_broker_data(file_path='data/broker_data.csv') -> pd.DataFrame:
    try:
        if not os.path.exists(file_path):
            logger.error(f"Broker data CSV file not found at path: {file_path}")
            return pd.DataFrame()
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()

        # Standardize 'zip_code', 'city', and 'state'
        for col in ['zip_code', 'city', 'state']:
            if col in df.columns:
                if col == 'city':
                    df[col] = df[col].str.title()
                elif col == 'state':
                    df[col] = df[col].str.upper()
                elif col == 'zip_code':
                    df[col] = df[col].astype(str)
            else:
                logger.warning(f"'{col}' column not found in Broker data.")

        return df
    except Exception as e:
        logger.error(f"Error loading Broker data: {e}")
        return pd.DataFrame()

# Load data at startup
zillow_data = load_zillow_data()
broker_data = load_broker_data()

# Extract unique cities
def get_unique_cities(df: pd.DataFrame) -> list:
    if 'city' in df.columns:
        return sorted(df['city'].dropna().unique())
    return []

unique_cities = get_unique_cities(zillow_data)
logger.info(f"Loaded {len(unique_cities)} unique cities from Zillow data.")

# Define allowed cities for trait matching
ALLOWED_CITIES = unique_cities  # Reuse the unique cities from Zillow data

# Helper function to sanitize data
def sanitize_data(obj):
    """
    Recursively replace NaN values with None and remove 'crawl_url_result' from dictionaries.
    """
    if isinstance(obj, list):
        return [sanitize_data(item) for item in obj]
    elif isinstance(obj, dict):
        obj.pop('crawl_url_result', None)
        return {k: sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj

# Helper function to extract SQL from OpenAI response
def extract_sql_from_response(response):
    """
    Extracts the SQL query from the OpenAI response.
    Removes any Markdown formatting or additional text.
    """
    try:
        # Remove any triple backticks and language identifiers
        sql = re.sub(r'^```sql\s*', '', response, flags=re.IGNORECASE)
        sql = re.sub(r'\s*```$', '', sql, flags=re.IGNORECASE)

        # Extract the first valid SQL statement using regex
        match = re.search(r'(SELECT[\s\S]+?;)', sql, re.IGNORECASE)
        if match:
            return match.group(1)
        else:
            # If no semicolon, assume the entire response is SQL
            return sql.strip()
    except Exception as e:
        logger.error(f"Error extracting SQL from response: {e}")
        return None

# # Helper function to extract feature from trait
# def extract_feature_from_trait(trait):
#     """
#     Extracts the relevant feature from the trait string by removing stopwords and matching 
#     remaining words against the features_list.
#     """
#     removal_phrases = ['has', 'a', 'the', 'an', 'is near', 'is a', 'is an']

#     # Remove removal phrases
#     for phrase in removal_phrases:
#         trait = trait.lower().replace(phrase, '')

#     # Tokenize and clean up the trait
#     tokens = [word for word in re.split(r'\W+', trait) if word]

#     # Join tokens back to form the cleaned trait
#     cleaned_trait = ' '.join(tokens)

#     return cleaned_trait.title()


# def extract_feature_from_trait(trait):
#     """
#     Extracts the relevant feature from the trait string by removing stopwords and matching 
#     remaining words against the features_list.
#     """
#     removal_phrases = ['has','the', 'an', 'is near']
#     # Tokenize the trait and remove unwanted words/phrases
#     for phrase in removal_phrases:
#         trait = trait.replace(phrase, '').strip()
    
#     # Tokenize and clean up the trait
#     tokens = [word.lower() for word in re.split(r'\W+', trait) if word]

#     # Join tokens back to form the cleaned trait
#     cleaned_trait = ' '.join(tokens)

#     # Return the cleaned trait
#     return cleaned_trait
import re

def extract_feature_from_trait(trait):
    """
    Extracts the relevant feature from the trait string by removing stopwords and matching 
    remaining words against the features_list.
    """
    removal_phrases = ['has', 'the', r'\ba\b', 'an', 'is near']
    
    # Tokenize the trait and remove unwanted words/phrases
    for phrase in removal_phrases:
        # Use regex to match the phrase as a whole word only
        trait = re.sub(rf'\b{phrase}\b', '', trait).strip()
    
    # Tokenize and clean up the trait
    tokens = [word.lower() for word in re.split(r'\W+', trait) if word]

    # Join tokens back to form the cleaned trait
    cleaned_trait = ' '.join(tokens)

    # Return the cleaned trait
    return cleaned_trait

# Initialize a simple in-memory cache for trait evaluations using Flask-Caching
def initialize_trait_cache():
    # Flask-Caching is already initialized as 'cache'
    pass  # No additional setup needed

initialize_trait_cache()

# Function to determine if a trait is matched, with caching
def is_trait_matched(property_record: dict, trait: str) -> str:
    """
    Determines if a property matches a given trait using OpenAI.
    
    Utilizes caching to avoid redundant API calls for the same property-trait pair.
    
    Parameters:
    - property_record (dict): A dictionary representing a property's details.
    - trait (str): The trait to evaluate.
    
    Returns:
    - str: 'yes', 'no', or 'unsure' based on the evaluation.
    """
    # Create a unique key for caching
    property_id = f"{property_record.get('zip_code', '')}_{property_record.get('price', '')}"
    cache_key = f"{property_id}_{trait.lower()}"

    # Check if result is cached
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    try:
        # Construct property details string
        relevant_columns = [
            'price', 'beds', 'baths', 'area', 'listing_agent', 'year_built',
            'property_tax', 'school_ratings', 'neighborhood_desc',
            'broker', 'city', 'state', 'zip_code', 'hoa_fees'
        ]

        property_details = "\n".join([
            f"{col.replace('_', ' ').title()}: {property_record.get(col, 'N/A')}"
            for col in relevant_columns
        ])

        prompt = (
        "You are an intelligent assistant specialized in real estate analysis. "
        "Given the detailed information about a property and a specific trait, determine whether the property satisfies the trait. "
        "If a property value is closely related to a trait even though it's not an exact match (e.g., 'redwood' instead of 'Redwood City'), map it accordingly. "
        "Respond with 'yes' if the trait fully matches, 'no' if it does not match, and 'unsure' if the information is incomplete or only partially matches.\n\n"
        "### Property Details:\n"
        f"{property_details}\n\n"
        "### Trait to Evaluate:\n"
        f"{trait}\n\n"
        "### Guidelines:\n"
        "- Respond with only one of the following options: 'yes', 'no', or 'unsure'. Do not include any additional text.\n"
        "- If the trait is clearly satisfied by the property details, respond with 'yes'.\n"
        "- If the trait is clearly not satisfied by the property details, respond with 'no'.\n"
        "- If the property details lack sufficient information to determine the trait, or if the match is partial, respond with 'unsure'.\n"
        "- For city-related traits, map any partial or misspelled city names to the correct full name from the allowed cities list.\n\n"
        "### Allowed Cities:\n"
        f"{', '.join(ALLOWED_CITIES)}\n\n"
        "### Examples:\n\n"
        "#### Example 1:\n"
        "**Property Details:**\n"
        "Price: 850000\n"
        "Beds: 3\n"
        "Baths: 2\n"
        "Area: 2000 sqft\n"
        "Listing Agent: Jane Doe\n"
        "Year Built: 1990\n"
        "Property Tax: 5000\n"
        "School Ratings: 8\n"
        "Neighborhood Desc: Spacious backyard with a swimming pool.\n"
        "Broker: XYZ Realty\n"
        "City: San Francisco\n"
        "State: CA\n"
        "Zip Code: 94118\n"
        "HOA Fees: 300\n\n"
        "**Trait:** Has a swimming pool.\n"
        "**Response:** yes\n\n"
        "#### Example 2:\n"
        "**Property Details:**\n"
        "Price: 600000\n"
        "Beds: 2\n"
        "Baths: 1\n"
        "Area: 1500 sqft\n"
        "Listing Agent: John Smith\n"
        "Year Built: 1985\n"
        "Property Tax: 4000\n"
        "School Ratings: 7\n"
        "Neighborhood Desc: Close to downtown parks.\n"
        "Broker: ABC Realty\n"
        "City: Irvine\n"
        "State: CA\n"
        "Zip Code: 92602\n"
        "HOA Fees: 250\n\n"
        "**Trait:** Includes a home gym.\n"
        "**Response:** no\n\n"
        "#### Example 3:\n"
        "**Property Details:**\n"
        "Price: 950000\n"
        "Beds: 4\n"
        "Baths: 3\n"
        "Area: 2500 sqft\n"
        "Listing Agent: Emily Clark\n"
        "Year Built: 2005\n"
        "Property Tax: 6000\n"
        "School Ratings: 9\n"
        "Neighborhood Desc: Recently renovated kitchen and hardwood floors.\n"
        "Broker: LMN Realty\n"
        "City: Redwood City\n"
        "State: CA\n"
        "Zip Code: 94061\n"
        "HOA Fees: 350\n\n"
        "**Trait:** Features hardwood floors.\n"
        "**Response:** yes\n\n"
        "#### Example 4:\n"
        "**Property Details:**\n"
        "Price: 720000\n"
        "Beds: 3\n"
        "Baths: 2\n"
        "Area: 1800 sqft\n"
        "Listing Agent: Michael Brown\n"
        "Year Built: 1995\n"
        "Property Tax: 4500\n"
        "School Ratings: 6\n"
        "Neighborhood Desc: Modern kitchen appliances.\n"
        "Broker: OPQ Realty\n"
        "City: Bronx\n"
        "State: NY\n"
        "Zip Code: 10451\n"
        "HOA Fees: 200\n\n"
        "**Trait:** Has a fireplace.\n"
        "**Response:** unsure\n\n"
        "#### Example 5 (Approximate City Match):\n"
        "**Property Details:**\n"
        "Price: 800000\n"
        "Beds: 3\n"
        "Baths: 2\n"
        "Area: 2200 sqft\n"
        "Listing Agent: Sarah Lee\n"
        "Year Built: 1998\n"
        "Property Tax: 5500\n"
        "School Ratings: 7\n"
        "Neighborhood Desc: Beautiful garden and modern kitchen.\n"
        "Broker: DEF Realty\n"
        "City: Redwood\n"
        "State: CA\n"
        "Zip Code: 94061\n"
        "HOA Fees: 320\n\n"
        "**Trait:** Located in Redwood City.\n"
        "**Response:** yes\n\n"
        "#### Example 6 (Misspelled City):\n"
        "**Property Details:**\n"
        "Price: 950000\n"
        "Beds: 4\n"
        "Baths: 3\n"
        "Area: 2600 sqft\n"
        "Listing Agent: Tom Hanks\n"
        "Year Built: 2000\n"
        "Property Tax: 6200\n"
        "School Ratings: 8\n"
        "Neighborhood Desc: Spacious living areas with hardwood floors.\n"
        "Broker: GHI Realty\n"
        "City: San Franciscso\n"
        "State: CA\n"
        "Zip Code: 94118\n"
        "HOA Fees: 400\n\n"
        "**Trait:** Located in San Francisco.\n"
        "**Response:** yes\n\n"
        "---\n\n"
        "### Now, evaluate the following:\n\n"
        "**Property Details:**\n"
        f"{property_details}\n\n"
        "**Trait:** {trait}\n"
        "**Response:**"
    )

        
        # Make the API call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3,
            temperature=0.0,
            stop=["\n"]
        )

        # Extract and clean the response
        trait_response = response['choices'][0]['message']['content'].strip().lower()

        # Validate the response
        if trait_response in ['yes', 'no', 'unsure']:
            cache.set(cache_key, trait_response)
            return trait_response
        else:
            # Default to 'unsure' if unexpected response
            cache.set(cache_key, 'unsure')
            return 'unsure'
    except Exception as e:
        logger.error(f"Error in is_trait_matched: {e}")
        return 'unsure'

# Helper function to extract user intent
def extract_user_intent(query):
    """
    Extracts user intent from the query using OpenAI.
    """
    try:
        user_intent_prompt = (
            "Analyze the following real estate query and extract the user intent. "
            "Provide the intent as a concise paragraph without any additional text or explanations."
            "If some location or keyword is incomplete, fill them with the most appropriate value from the data, e.g., replace 'redwood' with 'Redwood City'.\n\n"
            "### Example 1:\n"
            "**Query:** \"Looking for a 3 bedroom house with a big backyard in San Francisco.\"\n"
            "**User Intent:** The user is searching for a spacious three-bedroom house in San Francisco, prioritizing properties with large backyards. They likely value outdoor space for activities such as gardening or entertaining.\n\n"
            "### Example 2:\n"
            "**Query:** \"Seeking a 2 bedroom apartment near downtown Seattle with modern amenities.\"\n"
            "**User Intent:** The user is interested in a two-bedroom apartment near downtown Seattle, emphasizing modern amenities. They likely prioritize convenience and contemporary living spaces.\n\n"
            "### Example 3:\n"
            "**Query:** \"2 bed 2 bath in Irvine and 3 bed 2 bath in Redwood under 1600000.\"\n"
            "**User Intent:** The user is looking for both a 2-bedroom, 2-bathroom house in Irvine and a 3-bedroom, 2-bathroom property in Redwood City, with a combined budget under 1,600,000. They seek multiple options within a specific price range.\n\n"
            "### Example 4:\n"
            "**Query:** \"Looking for a 4-bedroom villa in Redwood with a pool and sea view, priced below 2 million.\"\n"
            "**User Intent:** The user desires a luxurious four-bedroom villa in Redwood City that includes a pool and offers a sea view, with a budget below 2 million. They prioritize luxury and scenic views.\n\n"
            "### Example 5:\n"
            "**Query:** \"Searching for 1 bed 1 bath condo in Redwood and 2 bed 2 bath townhouse in Boston under 750000.\"\n"
            "**User Intent:** The user is seeking both a 1-bedroom, 1-bathroom condo in Redwood City and a 2-bedroom, 2-bathroom townhouse in Boston, with a maximum budget of 750,000. They are interested in multiple property types across different cities within a specified price range.\n\n"
            "---\n\n"
            "**User Intent:**\n"
            f"{query}\n"
            "**User Intent:**"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": user_intent_prompt}
            ],
            max_tokens=150,
            temperature=0.0
        )
        user_intent = response['choices'][0]['message']['content'].strip()
        return user_intent
    except Exception as e:
        logger.error(f"Error extracting user intent: {e}")
        return None

# Helper function to extract traits
def extract_traits(user_intent, query):
    """
    Extracts traits from the user intent and query using OpenAI.
    """
    try:
        traits_prompt = (
            "From the following real estate query and user intent, extract the key traits."
            " Provide each trait starting with a verb phrase like 'is', 'has' and so on without any explanations or additional text."
            " Ensure that each trait is concise and relevant to the user's request."
            " Do not split numerical values like prices across multiple lines."
            " If multiple properties are mentioned, list each property separately and combine the budget where applicable."
            " Do not include any preamble, emojis, or phrases like 'Here are the extracted traits:'."
            " If it's not explicitly mentioned as a house or property, don't add that as a trait."
            " If some location or keyword is incomplete, fill them with the most appropriate value from the data, e.g., replace 'redwood' with 'Redwood City'."
            " Your response should only include the traits, exactly as in the examples, and nothing else.\n\n"
            "---\n\n"
            "**Example 1:**\n\n"
            "**User Intent:** The user is searching for a spacious three-bedroom house in San Francisco, prioritizing properties with large backyards. They likely value outdoor space for activities such as gardening or entertaining.\n\n"
            "**Query:** \"Looking for a 3 bedroom, 2 bathroom house with a big backyard in San Francisco.\"\n\n"
            "**Traits:**\n"
            "    is a house\n"
            "    has 3 bed, 2 bath\n"
            "    is in San Francisco\n"
            "    has a big backyard\n\n"
            "**Example 2:**\n\n"
            "**User Intent:** The user is interested in a two-bedroom apartment near downtown Seattle, emphasizing modern amenities. They likely prioritize convenience and contemporary living spaces.\n\n"
            "**Query:** \"Seeking a 2 bed 1 bath condo in downtown Seattle with modern amenities.\"\n\n"
            "**Traits:**\n"
            "    is a condo\n"
            "    has 2 bed, 1 bath\n"
            "    is in Seattle\n"
            "    has modern amenities\n\n"
            "**Example 3:**\n\n"
            "**User Intent:** The user is interested in finding a 2-bedroom, 2-bathroom property in Irvine and a 3-bedroom, 3-bathroom property in San Francisco, with a combined budget of $1,595,000.\n\n"
            "**Query:** \"2 bed 2 bath in Irvine and 3 bed 3 bath in San Francisco both under 1,595,000.\"\n\n"
            "**Traits:**\n"
            "    has 2 bed, 2 bath\n"
            "    is in Irvine\n"
            "    has 3 bed, 3 bath\n"
            "    is in San Francisco\n"
            "    is under $1,595,000.\n\n"
            "---\n\n"
            "**User Intent:**\n"
            f"{user_intent}\n\n"
            "**Query:**\n"
            f"\"{query}\"\n\n"
            "**Traits:**"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": traits_prompt}
            ],
            max_tokens=200,
            temperature=0.0
        )
        traits_response = response['choices'][0]['message']['content'].strip()
        traits = [trait.strip('- ').strip() for trait in traits_response.split('\n') if trait.strip()]
        return traits
    except Exception as e:
        logger.error(f"Error extracting traits: {e}")
        return []

# Helper function to extract key phrases
def extract_key_phrases(user_intent, traits, query):
    """
    Extracts key phrases from the user intent, traits, and query using OpenAI.
    """
    try:
        key_phrases_prompt = (
            "From the following real estate query, user intent, and traits, extract the top most relevant key phrases that can be used for search optimization or listing purposes."
            " Provide each key phrase on a separate line without any explanations or additional text."
            " Do not include any preamble, emojis, or phrases like 'Here are the top most relevant key phrases for search optimization or listing purposes:'."
            " If some location or keyword is incomplete, fill them with the most appropriate value from the data, e.g., replace 'redwood' with 'Redwood City'."
            " Your response should only include the key phrases, and structure it exactly as in the examples, and add no extra tokens.\n\n"
            "---\n\n"
            "**Example 1:**\n\n"
            "**User Intent:** The user is searching for a spacious three-bedroom house in San Francisco, prioritizing properties with large backyards. They likely value outdoor space for activities such as gardening or entertaining.\n\n"
            "**Traits:**\n"
            "    is a house\n"
            "    has 3 bed, 2 bath\n"
            "    is in San Francisco\n"
            "    has a big backyard\n\n"
            "**Query:** \"Looking for a 3 bedroom, 2 bathroom house with a big backyard in San Francisco.\"\n\n"
            "**Key Phrases:**\n"
            "3 bedroom house\n"
            "big backyard\n"
            "San Francisco real estate\n"
            "spacious home\n"
            "outdoor space\n"
            "family-friendly neighborhood\n"
            "gardening space\n"
            "entertainment area\n"
            "pet-friendly home\n"
            "modern amenities\n\n"
            "**Example 2:**\n\n"
            "**User Intent:** The user is interested in a two-bedroom apartment near downtown Seattle, emphasizing modern amenities. They likely prioritize convenience and contemporary living spaces.\n\n"
            "**Traits:**\n"
            "    is a condo\n"
            "    has 2 bed, 1 bath\n"
            "    is in Seattle\n"
            "    has modern amenities\n\n"
            "**Query:** \"Seeking a 2 bed 1 bath condo in downtown Seattle with modern amenities.\"\n\n"
            "**Key Phrases:**\n"
            "2 bedroom apartment\n"
            "downtown Seattle\n"
            "modern amenities\n"
            "urban living\n"
            "convenient location\n"
            "contemporary design\n"
            "city views\n"
            "public transportation access\n"
            "stylish interiors\n"
            "efficient layout\n\n"
            "---\n\n"
            "**User Intent:**\n"
            f"{user_intent}\n\n"
            "**Traits:**\n"
            f"{', '.join(traits)}\n\n"
            "**Query:**\n"
            f"\"{query}\"\n\n"
            "**Key Phrases:**"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": key_phrases_prompt}
            ],
            max_tokens=150,
            temperature=0.0,
            stop=["\n\n"]
        )
        key_phrases_response = response['choices'][0]['message']['content'].strip()
        key_phrases = [phrase.strip() for phrase in key_phrases_response.split('\n') if phrase.strip()]
        key_phrases = key_phrases[:10]  # Limit to top 10 key phrases
        return key_phrases
    except Exception as e:
        logger.error(f"Error extracting key phrases: {e}")
        return []

# Helper function to generate SQL query
def generate_sql_query(user_intent, traits, key_phrases, query):
    """
    Generates a SQL SELECT query based on user intent, traits, and key phrases using OpenAI.
    """
    try:
        unique_cities = zillow_data['city'].unique()
        sql_prompt = (
        "You are a SQL assistant specialized in real estate data. "
        "Based on the user's natural language query, user intent, traits, and key phrases, generate an accurate SQL query to search the properties. "
        "City and other dtring columns should be matched using LIKE instead of IN"
        "Map any broad location terms in the user's query to matching cities from the Available cities below . "
        "Ensure that all property features and filters mentioned in the query are accurately represented in the SQL. "
        "Use the following CSV columns for the 'zillow_data' table: 'price', 'beds', 'baths', 'area', 'listing_agent', 'year_built', "
        "'property_tax', 'school_ratings', 'neighborhood_desc', 'broker', 'city', 'state', 'zip_code',hoa_fees "
        "Use LIKE operators for string matching and ensure numeric comparisons are correctly handled. "
        "If the user specifies a broad location like 'Bay Area,' map it to matching cities present in Available cities below "
        "If some location or keyword is incomplete, fill them with the most appropriate value from the data, e.g., replace 'redwood' with 'Redwood City'. "
        "If no location is provided, don't add it as a filtering criterion. "
        "If certain values are not provided in the query, don't add them in the SQL query. "
        "If school rating is given as good in the query, use SQL condition as school_ratings >= 7. "
        "If school rating is given as excellent in the query, use SQL condition as school_ratings >= 8. "
        "When multiple conditions exist within the same column, combine them using OR and enclose them in parentheses. "
        "Combine conditions across different columns using AND. "
        "IMPORTANT: For all property features (e.g., 'pool', 'sea_view', 'hoa_fees', 'gym', 'rooftop_access', 'home_theater', 'wine_cellar', 'large_garden', 'high_ceiling', 'hardwood_floors', 'finished_basement', 'garage', 'exposed_brick_walls', 'spacious_backyard', 'solar_panels', 'panoramic_city_views', 'private_elevator', 'fireplace', 'swimming_pool'.etc), search within the 'neighborhood_desc' column using LIKE operators instead of using dedicated feature columns. "
        "Do NOT use separate columns like 'pool', 'gym', etc., for filtering features. Instead, encapsulate all feature-related filters within 'neighborhood_desc'. "
        "Return only the SQL query as plain text without any explanations, code fences, backticks, markdown formatting, or additional text.\n\n"

        "### Available Cities:\n"
        f"{unique_cities}\n\n"

        "### Example 1:\n"
        "**User Intent:** The user is searching for a spacious three-bedroom house in San Francisco, prioritizing properties with large backyards.\n"
        "**Traits:**\n"
        "- is a house\n"
        "  has 3 bed, 2 bath\n"
        "  is in San Francisco\n"
        "- has a big backyard\n"
        "**Key Phrases:**\n"
        "3 bedroom house\n"
        "big backyard\n"
        "San Francisco real estate\n"
        "spacious home\n"
        "outdoor space\n"
        "family-friendly neighborhood\n"
        "gardening space\n"
        "entertainment area\n"
        "pet-friendly home\n"
        "modern amenities\n\n"
        "**User Query:** \"Looking for a 3 bedroom, 2 bathroom house with a big backyard in San Francisco.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 3 AND baths = 2 AND city LIKE '%San Francisco%' AND (neighborhood_desc LIKE '%big backyard%');\n\n"

        
    
        "### Example 3:\n"
        "**User Intent:** The user wants a four-bedroom house in Miami with a pool and sea view, under a budget of $2 million.\n"
        "**Traits:**\n"
        "- is a house\n"
        "  has 4 bed, 3 bath\n"
        "  is in Miami\n"
        "- has a pool\n"
        "- has a sea view\n"
        "- is priced under $2,000,000\n"
        "**Key Phrases:**\n"
        "4 bedroom house\n"
        "pool\n"
        "sea view\n"
        "Miami real estate\n"
        "luxury home\n"
        "waterfront property\n"
        "family-friendly neighborhood\n"
        "modern design\n"
        "spacious backyard\n"
        "gated community\n\n"
        "**User Query:** \"Looking for a 4 bed 3 bath house in Miami with a pool and sea view, priced under 2 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 4 AND baths = 3 AND price <= 2000000 AND city LIKE '%Miami%' AND (neighborhood_desc LIKE '%pool%' OR neighborhood_desc LIKE '%sea view%');\n\n"

        "### Example 4:\n"
        "**User Intent:** The user is searching for a three-bedroom townhouse in Denver with low HOA fees and property taxes, priced below $700,000.\n"
        "**Traits:**\n"
        "- is a townhouse\n"
        "  has 3 bed, 2 bath\n"
        "  is in Denver\n"
        "- has low HOA fees\n"
        "- has low property taxes\n"
        "- is priced under $700,000\n"
        "**Key Phrases:**\n"
        "3 bedroom townhouse\n"
        "low HOA fees\n"
        "low property taxes\n"
        "Denver real estate\n"
        "budget-friendly\n"
        "family-friendly\n"
        "spacious living\n"
        "modern amenities\n"
        "central location\n"
        "pet-friendly\n\n"
        "**User Query:** \"Looking for a 3 bed 2 bath townhouse in Denver with low HOA fees and property taxes, priced under 700,000.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 3 AND baths = 2 AND price <= 700000 AND city LIKE '%Denver%' AND (neighborhood_desc LIKE '%low HOA fees%' OR neighborhood_desc LIKE '%low property taxes%');\n\n"

        "### Example 5:\n"
        "**User Intent:** The user wants a two-bedroom condo in San Francisco with a gym and rooftop access, priced below $1.2 million.\n"
        "**Traits:**\n"
        "- is a condo\n"
        "  has 2 bed, 2 bath\n"
        "  is in San Francisco\n"
        "- has a gym\n"
        "- has rooftop access\n"
        "- is priced under $1,200,000\n"
        "**Key Phrases:**\n"
        "2 bedroom condo\n"
        "gym\n"
        "rooftop access\n"
        "San Francisco real estate\n"
        "modern amenities\n"
        "urban living\n"
        "secure building\n"
        "pet-friendly\n"
        "spacious interiors\n"
        "high-rise building\n\n"
        "**User Query:** \"Looking for a 2 bed 2 bath condo in San Francisco with a gym and rooftop access, priced under 1.2 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 2 AND baths = 2 AND price <= 1200000 AND city LIKE '%San Francisco%' AND (neighborhood_desc LIKE '%gym%' OR neighborhood_desc LIKE '%rooftop access%');\n\n"

        "### Example 6:\n"
        "**User Intent:** The user is searching for a five-bedroom villa in Los Angeles with a home theater, wine cellar, and large garden, priced below $3 million.\n"
        "**Traits:**\n"
        "- is a villa\n"
        "  has 5 bed, 4 bath\n"
        "  is in Los Angeles\n"
        "- has a home theater\n"
        "- has a wine cellar\n"
        "- has a large garden\n"
        "- is priced under $3,000,000\n"
        "**Key Phrases:**\n"
        "5 bedroom villa\n"
        "home theater\n"
        "wine cellar\n"
        "large garden\n"
        "Los Angeles real estate\n"
        "luxury amenities\n"
        "spacious property\n"
        "gated community\n"
        "waterfront property\n"
        "exclusive neighborhood\n\n"
        "**User Query:** \"Looking for a 5 bed 4 bath villa in Los Angeles with a home theater, wine cellar, and large garden, priced under 3 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 5 AND baths = 4 AND price <= 3000000 AND city LIKE '%Los Angeles%' AND (neighborhood_desc LIKE '%home theater%' OR neighborhood_desc LIKE '%wine cellar%' OR neighborhood_desc LIKE '%large garden%');\n\n"

        "### Example 7:\n"
        "**User Intent:** The user wants a studio apartment in Redwood City with high ceilings and hardwood floors, priced below $900,000.\n"
        "**Traits:**\n"
        "- is a studio apartment\n"
        "  has 1 bed, 1 bath\n"
        "  is in Redwood City\n"
        "- has high ceilings\n"
        "- has hardwood floors\n"
        "- is priced under $900,000\n"
        "**Key Phrases:**\n"
        "studio apartment\n"
        "high ceilings\n"
        "hardwood floors\n"
        "Redwood City real estate\n"
        "modern design\n"
        "urban living\n"
        "pet-friendly\n"
        "open floor plan\n"
        "luxury finishes\n"
        "secure building\n\n"
        "**User Query:** \"Looking for a studio apartment in Redwood with high ceilings and hardwood floors, priced under 900,000.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 1 AND baths = 1 AND price <= 900000 AND city LIKE '%Redwood City%' AND (neighborhood_desc LIKE '%high ceilings%' OR neighborhood_desc LIKE '%hardwood floors%');\n\n"

        "### Example 8:\n"
        "**User Intent:** The user is searching for a three-bedroom duplex in Chicago with a finished basement and garage, priced below $1.5 million.\n"
        "**Traits:**\n"
        "- is a duplex\n"
        "  has 3 bed, 2 bath\n"
        "  is in Chicago\n"
        "- has a finished basement\n"
        "- has a garage\n"
        "- is priced under $1,500,000\n"
        "**Key Phrases:**\n"
        "3 bedroom duplex\n"
        "finished basement\n"
        "garage\n"
        "Chicago real estate\n"
        "spacious living\n"
        "family-friendly neighborhood\n"
        "modern amenities\n"
        "secure property\n"
        "close to schools\n"
        "well-maintained\n\n"
        "**User Query:** \"Looking for a 3 bed 2 bath duplex in Chicago with a finished basement and garage, priced under 1.5 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 3 AND baths = 2 AND price <= 1500000 AND city LIKE '%Chicago%' AND (neighborhood_desc LIKE '%finished basement%' OR neighborhood_desc LIKE '%garage%');\n\n"

        "### Example 9:\n"
        "**User Intent:** The user wants a two-bedroom loft in Boston with exposed brick walls and large windows, priced below $1.1 million.\n"
        "**Traits:**\n"
        "- is a loft\n"
        "  has 2 bed, 1 bath\n"
        "  is in Boston\n"
        "- has exposed brick walls\n"
        "- has large windows\n"
        "- is priced under $1,100,000\n"
        "**Key Phrases:**\n"
        "2 bedroom loft\n"
        "exposed brick walls\n"
        "large windows\n"
        "Boston real estate\n"
        "industrial design\n"
        "open floor plan\n"
        "modern amenities\n"
        "urban living\n"
        "pet-friendly\n"
        "high ceilings\n\n"
        "**User Query:** \"Looking for a 2 bed 1 bath loft in Boston with exposed brick walls and large windows, priced under 1.1 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 2 AND baths = 1 AND price <= 1100000 AND city LIKE '%Boston%' AND (neighborhood_desc LIKE '%exposed brick walls%' OR neighborhood_desc LIKE '%large windows%');\n\n"

        "### Example 10:\n"
        "**User Intent:** The user is searching for a four-bedroom ranch-style house in Phoenix with a spacious backyard and solar panels, priced below $850,000.\n"
        "**Traits:**\n"
        "- is a ranch-style house\n"
        "  has 4 bed, 3 bath\n"
        "  is in Phoenix\n"
        "- has a spacious backyard\n"
        "- has solar panels\n"
        "- is priced under $850,000\n"
        "**Key Phrases:**\n"
        "4 bedroom ranch-style house\n"
        "spacious backyard\n"
        "solar panels\n"
        "Phoenix real estate\n"
        "energy-efficient\n"
        "family-friendly neighborhood\n"
        "modern amenities\n"
        "secure property\n"
        "low maintenance\n"
        "pet-friendly\n\n"
        "**User Query:** \"Looking for a 4 bed 3 bath ranch-style house in Phoenix with a spacious backyard and solar panels, priced under 850,000.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 4 AND baths = 3 AND price <= 850000 AND city LIKE '%Phoenix%' AND (neighborhood_desc LIKE '%spacious backyard%' OR neighborhood_desc LIKE '%solar panels%');\n\n"

        "### Example 11:\n"
        "**User Intent:** The user wants a three-bedroom bungalow in Portland with a gourmet kitchen and hardwood floors, priced below $950,000.\n"
        "**Traits:**\n"
        "- is a bungalow\n"
        "  has 3 bed, 2 bath\n"
        "  is in Portland\n"
        "- has a gourmet kitchen\n"
        "- has hardwood floors\n"
        "- is priced under $950,000\n"
        "**Key Phrases:**\n"
        "3 bedroom bungalow\n"
        "gourmet kitchen\n"
        "hardwood floors\n"
        "Portland real estate\n"
        "modern amenities\n"
        "family-friendly neighborhood\n"
        "spacious living areas\n"
        "secure property\n"
        "pet-friendly\n"
        "well-maintained\n\n"
        "**User Query:** \"Looking for a 3 bed 2 bath bungalow in Portland with a gourmet kitchen and hardwood floors, priced under 950,000.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 3 AND baths = 2 AND price <= 950000 AND city LIKE '%Portland%' AND (neighborhood_desc LIKE '%gourmet kitchen%' OR neighborhood_desc LIKE '%hardwood floors%');\n\n"

        "### Example 12:\n"
        "**User Intent:** The user is searching for a duplex in Houston with energy-efficient appliances and a home office, priced below $1.3 million.\n"
        "**Traits:**\n"
        "- is a duplex\n"
        "  has 2 bed, 2 bath per unit\n"
        "  is in Houston\n"
        "- has energy-efficient appliances\n"
        "- has a home office\n"
        "- is priced under $1,300,000\n"
        "**Key Phrases:**\n"
        "duplex\n"
        "energy-efficient appliances\n"
        "home office\n"
        "Houston real estate\n"
        "modern amenities\n"
        "spacious interiors\n"
        "family-friendly neighborhood\n"
        "secure property\n"
        "pet-friendly\n"
        "well-maintained\n\n"
        "**User Query:** \"Looking for a duplex in Houston with energy-efficient appliances and a home office, priced under 1.3 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE type = 'duplex' AND price <= 1300000 AND city LIKE '%Houston%' AND (neighborhood_desc LIKE '%energy-efficient appliances%' OR neighborhood_desc LIKE '%home office%');\n\n"

        "### Example 13:\n"
        "**User Intent:** The user wants a five-bedroom farmhouse in Nashville with a barn, landscaped garden, and solar energy system, priced below $2.2 million.\n"
        "**Traits:**\n"
        "- is a farmhouse\n"
        "  has 5 bed, 4 bath\n"
        "  is in Nashville\n"
        "- has a barn\n"
        "- has a landscaped garden\n"
        "- has a solar energy system\n"
        "- is priced under $2,200,000\n"
        "**Key Phrases:**\n"
        "5 bedroom farmhouse\n"
        "barn\n"
        "landscaped garden\n"
        "solar energy system\n"
        "Nashville real estate\n"
        "luxury amenities\n"
        "spacious property\n"
        "family-friendly neighborhood\n"
        "modern amenities\n"
        "energy-efficient\n\n"
        "**User Query:** \"Looking for a 5 bed 4 bath farmhouse in Nashville with a barn, landscaped garden, and solar energy system, priced under 2.2 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 5 AND baths = 4 AND price <= 2200000 AND city LIKE '%Nashville%' AND (neighborhood_desc LIKE '%barn%' OR neighborhood_desc LIKE '%landscaped garden%' OR neighborhood_desc LIKE '%solar energy system%');\n\n"

        "### Example 14:\n"
        "**User Intent:** The user is searching for a two-bedroom penthouse in Dallas with panoramic city views and a private elevator, priced below $1.8 million.\n"
        "**Traits:**\n"
        "- is a penthouse\n"
        "  has 2 bed, 2 bath\n"
        "  is in Dallas\n"
        "- has panoramic city views\n"
        "- has a private elevator\n"
        "- is priced under $1,800,000\n"
        "**Key Phrases:**\n"
        "2 bedroom penthouse\n"
        "panoramic city views\n"
        "private elevator\n"
        "Dallas real estate\n"
        "luxury amenities\n"
        "high-rise living\n"
        "secure building\n"
        "modern design\n"
        "spacious interiors\n"
        "pet-friendly\n\n"
        "**User Query:** \"Looking for a 2 bed 2 bath penthouse in Dallas with panoramic city views and a private elevator, priced under 1.8 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 2 AND baths = 2 AND price <= 1800000 AND city LIKE '%Dallas%' AND (neighborhood_desc LIKE '%panoramic city views%' OR neighborhood_desc LIKE '%private elevator%');\n\n"

        "### Example 15:\n"
        "**User Intent:** The user wants a three-bedroom colonial-style house in Philadelphia with a fireplace, home theater, and swimming pool, priced below $1.4 million.\n"
        "**Traits:**\n"
        "- is a colonial-style house\n"
        "  has 3 bed, 2 bath\n"
        "  is in Philadelphia\n"
        "- has a fireplace\n"
        "- has a home theater\n"
        "- has a swimming pool\n"
        "- is priced under $1,400,000\n"
        "**Key Phrases:**\n"
        "3 bedroom colonial-style house\n"
        "fireplace\n"
        "home theater\n"
        "swimming pool\n"
        "Philadelphia real estate\n"
        "modern amenities\n"
        "spacious backyard\n"
        "family-friendly neighborhood\n"
        "secure property\n"
        "pet-friendly\n\n"
        "**User Query:** \"Looking for a 3 bed 2 bath colonial-style house in Philadelphia with a fireplace, home theater, and swimming pool, priced under 1.4 million.\"\n\n"
        "**SQL Query:**\n"
        "SELECT * FROM zillow_data WHERE beds = 3 AND baths = 2 AND price <= 1400000 AND city LIKE '%Philadelphia%' AND (neighborhood_desc LIKE '%fireplace%' OR neighborhood_desc LIKE '%home theater%' OR neighborhood_desc LIKE '%swimming pool%');\n\n"

        "---\n\n"
        "**User Intent:**\n"
        f"{user_intent}\n\n"
        "**Traits:**\n"
        f"{traits}\n\n"
        "**Key Phrases:**\n"
        f"{key_phrases}\n\n"
        "**User Query:**\n"
        f"\"{query}\"\n\n"
        "**SQL Query:**"
    )
       
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": sql_prompt}
            ],
            max_tokens=150,
            temperature=0.0
        )
        sql_response = response['choices'][0]['message']['content'].strip()
        sql_query = extract_sql_from_response(sql_response)
        if not sql_query:
            logger.error("Failed to extract SQL query from OpenAI response.")
            return None
        logger.info(f"Generated SQL Query: {sql_query}")
        # Validate SQL starts with SELECT
        if not sql_query.upper().startswith("SELECT"):
            logger.error("Invalid SQL query generated.")
            return None
        return sql_query
    except Exception as e:
        logger.error(f"Error generating SQL query: {e}")
        return None

# Helper function to execute SQL query
def execute_sql_query(sql_query):
    """
    Executes the SQL query against the zillow_data DataFrame.
    """
    try:
        result_df = psql.sqldf(sql_query, {'zillow_data': zillow_data})
        result = result_df.to_dict(orient='records')
        logger.info(f"SQL Query Executed Successfully. Number of Results: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return None

# Helper function to generate property keywords
def generate_property_keywords(query, user_intent, traits, key_phrases, sql_query):
    """
    Generates property keywords based on the provided information using OpenAI.
    """
    try:
        property_keywords_prompt = (
            "Analyze the following real estate query, user intent, traits, key phrases, and SQL query to extract the values used for each column in the SQL statement."
            " Do not miss any content or value from SQL."
            " Format the output as a comma-separated list in the format 'Column: Value'. But don't add any extra piece of text."
            " Ensure that each value corresponds accurately to the SQL query."
            " IMPORTANT: Only give precise output in the format given without any additional text or tokens."
            " If some location or keyword is incomplete, fill them with the most appropriate value from the data, e.g., replace 'redwood' with 'Redwood City'."
            " Do not include any explanations or additional text.\n\n"

            "### Query:\n"
            f"\"{query}\"\n\n"

            "### User Intent:\n"
            f"{user_intent}\n\n"

            "### Traits:\n"
            f"{', '.join(traits)}\n\n"

            "### Key Phrases:\n"
            f"{', '.join(key_phrases)}\n\n"

            "### SQL Query:\n"
            f"{sql_query}\n\n"

            "### PropertyKeywords:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are ChatGPT, a large language model trained by OpenAI."},
                {"role": "user", "content": property_keywords_prompt}
            ],
            max_tokens=100,
            temperature=0.0,
            stop=["\n\n"]
        )
        property_keywords = response['choices'][0]['message']['content'].strip()
        if not property_keywords:
            property_keywords = "No keywords generated."
        logger.info(f"Generated Property Keywords: {property_keywords}")
        return property_keywords
    except Exception as e:
        logger.error(f"Error generating property keywords: {e}")
        return "No keywords generated."

# Helper function to handle dynamic columns with dots logic
def handle_dynamic_columns(result, traits):
    """
    Adds dynamic columns to each record in the result based on traits.
    Marks presence with '🟢', '🟡', or '⚪'.
    """
    for trait in traits:
        # Generate a concise column name from the trait
        column_name = extract_feature_from_trait(trait)
        # Ensure unique column names
        original_column_name = column_name
        counter = 1
        while column_name in result[0]:
            column_name = f"{original_column_name}_{counter}"
            counter += 1
        # Add dynamic column to result
        for record in result:
            # Use the 'is_trait_matched' function to determine the status
            match_status = is_trait_matched(record, trait)
            # Assign the appropriate colored dot
            if match_status == 'yes':
                record[column_name] = "🟢"
            elif match_status == 'unsure':
                record[column_name] = "🟡"
            else:
                record[column_name] = "⚪"
    return result

# Route: /api/search
@app.route('/api/search', methods=['POST'])
def search():
    """
    Comprehensive search endpoint that takes a user query, extracts information, generates SQL,
    executes SQL, generates property keywords, and compiles the response.
    """
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'No query provided.'}), 400

    try:
        # Step 1: Extract User Intent
        user_intent = extract_user_intent(query)
        if not user_intent:
            return jsonify({'error': 'Failed to extract user intent.'}), 500

        # Step 2: Extract Traits
        traits = extract_traits(user_intent, query)
        if not traits:
            return jsonify({'error': 'Failed to extract traits.'}), 500

        # Step 3: Extract Key Phrases
        key_phrases = extract_key_phrases(user_intent, traits, query)
        if not key_phrases:
            return jsonify({'error': 'Failed to extract key phrases.'}), 500

        # Step 4: Generate SQL Query
        sql_query = generate_sql_query(user_intent, traits, key_phrases, query)
        if not sql_query:
            return jsonify({'error': 'Failed to generate SQL query.'}), 500

        # Step 5: Execute SQL Query
        result = execute_sql_query(sql_query)
        if result is None:
            return jsonify({'error': 'Failed to execute SQL query.'}), 500

        # Step 6: Generate Property Keywords
        property_keywords = generate_property_keywords(query, user_intent, traits, key_phrases, sql_query)

        # Step 7: Handle Dynamic Columns with Dots Logic
        if result:
            result = handle_dynamic_columns(result, traits)
        else:
            logger.info("No results to process for dynamic columns.")

        # Step 8: Sanitize Data
        sanitized_result = sanitize_data(result)

        # Step 9: Extract Dynamic Columns
        dynamic_columns = [extract_feature_from_trait(trait) for trait in traits]



        # Step 9: Compile Response
        response = OrderedDict()
        response['query'] = query
        response['user_intent'] = user_intent
        response['traits'] = traits
        response['key_phrases'] = key_phrases
        response['property_keywords'] = property_keywords
        response['sql_query'] = sql_query
        response['result'] = sanitized_result
        # After handle_dynamic_columns
        response['dynamic_columns'] = dynamic_columns

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unhandled exception in /api/search: {e}")
        return jsonify({'error': 'Internal server error.'}), 500



# # Route: /api/save_search
# @app.route('/api/save_search', methods=['POST'])
# def save_search():
#     """
#     Save a new search query.
#     Expects JSON payload with 'search' field.
#     """
#     data = request.get_json()
#     search = data.get('search', '').strip()

#     if not search:
#         return jsonify({'error': 'No search query provided.'}), 400

#     try:
#         # Retrieve existing saved searches from cache
#         saved_searches = cache.get('saved_searches') or []

#         if search in saved_searches:
#             return jsonify({'message': 'Search already saved.'}), 200

#         # Append the new search
#         saved_searches.append(search)

#         # Update the cache
#         cache.set('saved_searches', saved_searches)

#         logger.info(f"Saved new search: {search}")

#         return jsonify({'message': 'Search saved successfully.'}), 200

#     except Exception as e:
#         logger.error(f"Error saving search: {e}")
#         return jsonify({'error': 'Failed to save search.'}), 500

# # Route: /api/get_saved_searches
# @app.route('/api/get_saved_searches', methods=['GET'])
# def get_saved_searches():
#     """
#     Retrieve all saved searches.
#     """
#     try:
#         saved_searches = cache.get('saved_searches') or []
#         return jsonify({'saved_searches': saved_searches}), 200
#     except Exception as e:
#         logger.error(f"Error retrieving saved searches: {e}")
#         return jsonify({'error': 'Failed to retrieve saved searches.'}), 500

# # Route: /api/delete_saved_search
# @app.route('/api/delete_saved_search', methods=['POST'])
# def delete_saved_search():
#     """
#     Delete a specific search query.
#     Expects JSON payload with 'search' field.
#     """
#     data = request.get_json()
#     search = data.get('search', '').strip()

#     if not search:
#         return jsonify({'error': 'No search query provided.'}), 400

#     try:
#         saved_searches = cache.get('saved_searches') or []

#         if search not in saved_searches:
#             return jsonify({'error': 'Search not found.'}), 404

#         # Remove the search
#         saved_searches.remove(search)

#         # Update the cache
#         cache.set('saved_searches', saved_searches)

#         logger.info(f"Deleted search: {search}")

#         return jsonify({'message': 'Search deleted successfully.'}), 200

#     except Exception as e:
#         logger.error(f"Error deleting search: {e}")
#         return jsonify({'error': 'Failed to delete search.'}), 500

# # Route: /api/clear_saved_searches
# @app.route('/api/clear_saved_searches', methods=['POST'])
# def clear_saved_searches():
#     """
#     Clear all saved searches.
#     """
#     try:
#         cache.set('saved_searches', [])
#         logger.info("Cleared all saved searches.")
#         return jsonify({'message': 'All saved searches cleared.'}), 200
#     except Exception as e:
#         logger.error(f"Error clearing saved searches: {e}")
#         return jsonify({'error': 'Failed to clear saved searches.'}), 500
# Route: /api/save_search
@app.route('/api/save_search', methods=['POST'])
def save_search():
    """
    Save a new search query along with its response.
    Expects JSON payload with 'search' and 'response' fields.
    """
    data = request.get_json()
    search = data.get('search', '').strip()
    response_data = data.get('response', {})

    if not search:
        return jsonify({'error': 'No search query provided.'}), 400

    try:
        # Retrieve existing saved searches from cache
        saved_searches = cache.get('saved_searches') or []

        # Check if the search already exists
        if any(entry['search'] == search for entry in saved_searches):
            return jsonify({'message': 'Search already saved.'}), 200

        # Append the new search with its response
        saved_searches.append({'search': search, 'response': response_data})

        # Update the cache
        cache.set('saved_searches', saved_searches)

        logger.info(f"Saved new search: {search}")

        return jsonify({'message': 'Search saved successfully.'}), 200

    except Exception as e:
        logger.error(f"Error saving search: {e}")
        return jsonify({'error': 'Failed to save search.'}), 500

# Route: /api/get_saved_searches
@app.route('/api/get_saved_searches', methods=['GET'])
def get_saved_searches():
    """
    Retrieve all saved searches along with their responses.
    """
    try:
        saved_searches = cache.get('saved_searches') or []
        return jsonify({'saved_searches': saved_searches}), 200
    except Exception as e:
        logger.error(f"Error retrieving saved searches: {e}")
        return jsonify({'error': 'Failed to retrieve saved searches.'}), 500

# Route: /api/delete_saved_search
@app.route('/api/delete_saved_search', methods=['POST'])
def delete_saved_search():
    """
    Delete a specific search query.
    Expects JSON payload with 'search' field.
    """
    data = request.get_json()
    search = data.get('search', '').strip()

    if not search:
        return jsonify({'error': 'No search query provided.'}), 400

    try:
        saved_searches = cache.get('saved_searches') or []

        # Find the search entry
        search_entry = next((entry for entry in saved_searches if entry['search'] == search), None)

        if not search_entry:
            return jsonify({'error': 'Search not found.'}), 404

        # Remove the search entry
        saved_searches.remove(search_entry)

        # Update the cache
        cache.set('saved_searches', saved_searches)

        logger.info(f"Deleted search: {search}")

        return jsonify({'message': 'Search deleted successfully.'}), 200

    except Exception as e:
        logger.error(f"Error deleting search: {e}")
        return jsonify({'error': 'Failed to delete search.'}), 500

# Route: /api/clear_saved_searches
@app.route('/api/clear_saved_searches', methods=['POST'])
def clear_saved_searches():
    """
    Clear all saved searches.
    """
    try:
        cache.set('saved_searches', [])
        logger.info("Cleared all saved searches.")
        return jsonify({'message': 'All saved searches cleared.'}), 200
    except Exception as e:
        logger.error(f"Error clearing saved searches: {e}")
        return jsonify({'error': 'Failed to clear saved searches.'}), 500


# Route: /api/get_broker_details
@app.route('/api/get_broker_details', methods=['GET'])
def get_broker_details_route():
    """
    Retrieve broker details based on the provided zip code.
    Expects 'zip_code' as a query parameter.
    """
    zip_code = request.args.get('zip_code', '').strip()

    if not zip_code:
        return jsonify({'error': 'No zip_code provided.'}), 400

    try:
        # Filter brokers by zip code
        filtered_brokers = broker_data[broker_data['zip_code'] == zip_code]

        if filtered_brokers.empty:
            logger.info(f"No brokers found for zip code: {zip_code}")
            return jsonify({'message': f'No brokers found for zip code: {zip_code}'}), 404

        # Select and rename columns for better readability
        display_brokers = filtered_brokers.rename(columns={
            'broker': 'Broker Name',
            'zip_code': 'Zip Code',
            'city': 'City',
            'state': 'State',
            'reviews': 'Reviews',
            'recent_homes_sold': 'Recent Homes Sold',
            'negotiations_done': 'Negotiations Done',
            'years_of_experience': 'Years of Experience',
            'rating': 'Rating'
        })[['Broker Name', 'City', 'State', 'Zip Code', 'Reviews', 'Recent Homes Sold', 'Negotiations Done', 'Years of Experience', 'Rating']]

        # Convert to list of dictionaries
        brokers_list = display_brokers.to_dict(orient='records')

        return jsonify({'brokers': brokers_list}), 200

    except Exception as e:
        logger.error(f"Error retrieving broker details: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

# Route: /api/save_to_txt
@app.route('/api/save_to_txt', methods=['POST'])
def save_to_txt_route():
    """
    Save the input query, user intent, traits, key phrases, PropertyKeywords, SQL query, and final output to a text file.
    Expects JSON payload with 'query', 'user_intent', 'traits', 'key_phrases', 'property_keywords', 'sql_query', 'result'.
    """
    data = request.get_json()
    query = data.get('query', '').strip()
    user_intent = data.get('user_intent', '').strip()
    traits = data.get('traits', [])
    key_phrases = data.get('key_phrases', [])
    property_keywords = data.get('property_keywords', '').strip()
    sql_query = data.get('sql_query', '').strip()
    result = data.get('result', [])

    if not all([query, user_intent, traits, key_phrases, property_keywords, sql_query]):
        return jsonify({'error': 'Incomplete data provided.'}), 400

    try:
        with open('query_output.txt', 'w') as file:
            file.write(f"Input Query: {query}\n\n")
            file.write(f"User Intent: {user_intent}\n\n")
            file.write(f"Traits: {', '.join(traits)}\n\n")
            file.write(f"Key Phrases: {', '.join(key_phrases)}\n\n")
            file.write(f"PropertyKeywords: {property_keywords}\n\n")
            file.write(f"Generated SQL Query: {sql_query}\n\n")
            if result:
                file.write(f"Final Output from CSV:\n")
                for record in result:
                    file.write(f"{record}\n")
            else:
                file.write("Final Output from CSV: No results found.\n\n")

        logger.info("Results saved to query_output.txt successfully.")
        return jsonify({'message': 'Results saved to query_output.txt'}), 200

    except Exception as e:
        logger.error(f"Error saving results to text file: {e}")
        return jsonify({'error': 'Failed to save results.'}), 500

# Route: /api/extract_information (Optional)
@app.route('/api/extract_information', methods=['POST'])
def extract_information_route():
    """
    Extract user intent, traits, and key phrases from the input query using OpenAI.
    Expects JSON payload with 'query' field.
    """
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'No query provided.'}), 400

    try:
        # Extract User Intent
        user_intent = extract_user_intent(query)
        if not user_intent:
            return jsonify({'error': 'Failed to extract user intent.'}), 500

        # Extract Traits
        traits = extract_traits(user_intent, query)
        if not traits:
            return jsonify({'error': 'Failed to extract traits.'}), 500

        # Extract Key Phrases
        key_phrases = extract_key_phrases(user_intent, traits, query)
        if not key_phrases:
            return jsonify({'error': 'Failed to extract key phrases.'}), 500

        # Compile Response
        response = OrderedDict()
        response['user_intent'] = user_intent
        response['traits'] = traits
        response['key_phrases'] = key_phrases

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unhandled exception in /api/extract_information: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

# Run the Flask app
if __name__ == '__main__':
    try:
        app.run(debug=True, port=5001)
    except Exception as e:
        logger.error(f"Failed to start the Flask app: {e}")
        exit(1)

