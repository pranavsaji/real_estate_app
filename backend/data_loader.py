# backend/data_loader.py

import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def load_zillow_data(file_path='data/Zillow_Data.csv') -> pd.DataFrame:
    try:
        if not os.path.exists(file_path):
            logger.error(f"Zillow data CSV file not found at path: {file_path}")
            return pd.DataFrame()
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip().str.lower()
        df = df.loc[:, ~df.columns.duplicated()] 

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

        # Ensure 'property_name', 'image_url', and 'listingUrl' exist
        if 'property_name' not in df.columns:
            df['property_name'] = df.get('address', 'Property')  # Replace with actual logic
            logger.warning("'property_name' column not found. Using 'address' or default value.")
        if 'image_url' not in df.columns:
            df['image_url'] = 'https://via.placeholder.com/150'  # Placeholder image
            logger.warning("'image_url' column not found. Using placeholder images.")
        if 'listingUrl' not in df.columns:
            df['listingUrl'] = 'https://www.zillow.com/'  # Placeholder link
            logger.warning("'listingUrl' column not found. Using placeholder links.")

        return df
    except Exception as e:
        logger.error(f"Error loading Zillow data: {e}")
        return pd.DataFrame()

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

# Load data at module import
zillow_data = load_zillow_data()
broker_data = load_broker_data()

def get_unique_cities(df: pd.DataFrame) -> list:
    """
    Extracts a sorted list of unique cities from the provided DataFrame.
    """
    if 'city' in df.columns:
        return sorted(df['city'].dropna().unique())
    return []
