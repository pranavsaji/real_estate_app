# backend/carousel.py

import os
import requests
import logging
from flask import Blueprint, request, jsonify
from utils import (
    extract_user_intent,
    extract_traits,
    extract_key_phrases,
    generate_sql_query,
    execute_sql_query,
    sanitize_data
)

carousel_api = Blueprint('carousel_api', __name__)
logger = logging.getLogger(__name__)

# Pinnacle API Configuration
PINNACLE_API_URL = "https://www.trypinnacle.dev/api/send/rcs"  # Corrected API endpoint
PINNACLE_API_KEY = os.getenv("PINNACLE_API_KEY")  # Ensure this is set in your .env

@carousel_api.route('/api/send_carousel', methods=['POST'])
def send_carousel():
    """
    API endpoint to create and send a carousel of properties via RCS.
    Expects a JSON payload with a 'query' and 'phone_number'.
    """
    data = request.get_json()
    query = data.get('query', '').strip()
    phone_number = data.get('phone_number', '').strip()

    if not query or not phone_number:
        logger.warning("Missing 'query' or 'phone_number' in the request payload.")
        return jsonify({'error': 'Query and phone_number are required.'}), 400

    try:
        # Step 1: Extract User Intent
        user_intent = extract_user_intent(query)
        if not user_intent:
            logger.error("Failed to extract user intent from the query.")
            return jsonify({'error': 'Failed to extract user intent.'}), 500

        # Step 2: Extract Traits
        traits = extract_traits(user_intent, query)
        if not traits:
            logger.error("Failed to extract traits from the query.")
            return jsonify({'error': 'Failed to extract traits.'}), 500

        # Step 3: Extract Key Phrases
        key_phrases = extract_key_phrases(user_intent, traits, query)
        if not key_phrases:
            logger.error("Failed to extract key phrases from the query.")
            return jsonify({'error': 'Failed to extract key phrases.'}), 500

        # Step 4: Generate SQL Query
        sql_query = generate_sql_query(user_intent, traits, key_phrases, query)
        if not sql_query:
            logger.error("Failed to generate SQL query based on the extracted traits and key phrases.")
            return jsonify({'error': 'Failed to generate SQL query.'}), 500

        logger.info(f"Generated SQL Query: {sql_query}")

        # Step 5: Execute SQL Query
        result = execute_sql_query(sql_query)
        if result is None:
            logger.error("SQL query execution failed.")
            return jsonify({'error': 'Failed to execute SQL query.'}), 500

        logger.info(f"SQL Query Executed Successfully. Number of Results: {len(result)}")

        # Step 6: Sanitize Data
        sanitized_result = sanitize_data(result)

        # **Debug Log: Print sanitized_result**
        logger.debug(f"Sanitized Result: {sanitized_result}")

        if not sanitized_result:
            logger.warning("No properties found matching the query after sanitization.")
            return jsonify({'error': 'No properties found matching the query.'}), 404

        # Step 7: Select Top 5 Properties
        top_properties = sanitized_result[:5]

        # Step 8: Create Carousel Items
        carousel_items = []
        for prop in top_properties:
            # **Debug Log: Check property keys**
            logger.debug(f"Processing Property ID {prop.get('id')}: Keys - {prop.keys()}")

            # Safely retrieve each field with fallback options
            property_name = prop.get("property_name") or prop.get("address") or "Property"
            if not prop.get("property_name") and not prop.get("address"):
                logger.warning(f"Property ID {prop.get('id')} is missing both 'property_name' and 'address'.")

            # Initialize the carousel item with mandatory fields
            item = {
                "title": property_name,
                "description": f"Price: ${prop.get('price', 'N/A')}\nBeds: {prop.get('beds', 'N/A')}\nBaths: {prop.get('baths', 'N/A')}",
            }

            # Conditionally add 'mediaUrl' if it exists
            media_url = prop.get("image_url") or prop.get("media_url")  # Adjust based on actual data
            if media_url:
                item["mediaUrl"] = media_url
            else:
                logger.warning(f"Property ID {prop.get('id')} is missing 'image_url'.")

            # Conditionally add 'cards' if 'listingUrl' exists and is valid
            listing_url = prop.get("listingUrl")
            if listing_url and listing_url != "#":
                item["cards"] = [{
                    "type": "open_url",
                    "url": listing_url,
                    "label": "View Listing"
                }]
            else:
                logger.warning(f"Property ID {prop.get('id')} is missing 'listingUrl' or it is invalid.")

            carousel_items.append(item)

        # **Debug Log: Print carousel_items**
        logger.debug(f"Carousel Items: {carousel_items}")

        if not carousel_items:
            logger.error("No carousel items to send after processing properties.")
            return jsonify({'error': 'No valid carousel items to send.'}), 500

        # Step 9: Prepare Carousel Payload for Pinnacle API
        carousel_payload = {
            "from": "test",  # Use 'test' for sending from the Pinnacle test agent
            "to": phone_number,
            "cards": carousel_items  # Only include 'cards' to comply with API requirements
            # "text": "Here are some properties that match your search:"  # Omit 'text' when using 'cards'
        }

        # **Debug Log: Print carousel_payload**
        logger.debug(f"Carousel Payload: {carousel_payload}")

        # Step 10: Send Carousel via Pinnacle API
        headers = {
            "PINNACLE-API-Key": PINNACLE_API_KEY,  # As per API documentation
            "Content-Type": "application/json"
        }

        response = requests.post(PINNACLE_API_URL, json=carousel_payload, headers=headers)

        if response.status_code == 200:
            logger.info(f"Carousel sent successfully to {phone_number}. Response: {response.json()}")
            return jsonify({'message': 'Carousel sent successfully.'}), 200
        else:
            logger.error(f"Failed to send carousel. Status Code: {response.status_code}, Response: {response.text}")
            return jsonify({'error': 'Failed to send carousel.'}), 500

    except Exception as e:
        logger.exception(f"Unhandled exception in /api/send_carousel: {e}")
        return jsonify({'error': 'Internal server error.'}), 500

# # backend/carousel.py

# import os
# import requests
# import logging
# from flask import Blueprint, request, jsonify
# from utils import (
#     extract_user_intent,
#     extract_traits,
#     extract_key_phrases,
#     generate_sql_query,
#     execute_sql_query,
#     sanitize_data
# )

# carousel_api = Blueprint('carousel_api', __name__)
# logger = logging.getLogger(__name__)

# # Pinnacle API Configuration
# PINNACLE_API_URL = "https://www.trypinnacle.dev/api/send/rcs"  
# PINNACLE_API_KEY = os.getenv("PINNACLE_API_KEY") 

# @carousel_api.route('/api/send_carousel', methods=['POST'])
# def send_carousel():
#     """
#     API endpoint to create and send a carousel of properties via RCS.
#     Expects a JSON payload with a 'query' and 'phone_number'.
#     """
#     data = request.get_json()
#     query = data.get('query', '').strip()
#     phone_number = data.get('phone_number', '').strip()

#     if not query or not phone_number:
#         logger.warning("Missing 'query' or 'phone_number' in the request payload.")
#         return jsonify({'error': 'Query and phone_number are required.'}), 400

#     try:
#         # Step 1: Extract User Intent
#         user_intent = extract_user_intent(query)
#         if not user_intent:
#             logger.error("Failed to extract user intent from the query.")
#             return jsonify({'error': 'Failed to extract user intent.'}), 500

#         # Step 2: Extract Traits
#         traits = extract_traits(user_intent, query)
#         if not traits:
#             logger.error("Failed to extract traits from the query.")
#             return jsonify({'error': 'Failed to extract traits.'}), 500

#         # Step 3: Extract Key Phrases
#         key_phrases = extract_key_phrases(user_intent, traits, query)
#         if not key_phrases:
#             logger.error("Failed to extract key phrases from the query.")
#             return jsonify({'error': 'Failed to extract key phrases.'}), 500

#         # Step 4: Generate SQL Query
#         sql_query = generate_sql_query(user_intent, traits, key_phrases, query)
#         if not sql_query:
#             logger.error("Failed to generate SQL query based on the extracted traits and key phrases.")
#             return jsonify({'error': 'Failed to generate SQL query.'}), 500

#         logger.info(f"Generated SQL Query: {sql_query}")

#         # Step 5: Execute SQL Query
#         result = execute_sql_query(sql_query)
#         if result is None:
#             logger.error("SQL query execution failed.")
#             return jsonify({'error': 'Failed to execute SQL query.'}), 500

#         logger.info(f"SQL Query Executed Successfully. Number of Results: {len(result)}")

#         # Step 6: Sanitize Data
#         sanitized_result = sanitize_data(result)

#         # **Debug Log: Print sanitized_result**
#         logger.debug(f"Sanitized Result: {sanitized_result}")

#         if not sanitized_result:
#             logger.warning("No properties found matching the query after sanitization.")
#             return jsonify({'error': 'No properties found matching the query.'}), 404

#         # Step 7: Select Top 5 Properties
#         top_properties = sanitized_result[:5]

#         # Step 8: Create Carousel Items
#         carousel_items = []
#         for prop in top_properties:
#             # **Debug Log: Check property keys**
#             logger.debug(f"Processing Property ID {prop.get('id')}: Keys - {prop.keys()}")

#             # Safely retrieve each field with fallback options
#             property_name = prop.get("property_name") or prop.get("address") or "Property"
#             if not prop.get("property_name") and not prop.get("address"):
#                 logger.warning(f"Property ID {prop.get('id')} is missing both 'property_name' and 'address'.")

#             # Initialize the carousel item with mandatory fields
#             item = {
#                 "title": property_name,
#                 "description": f"Price: ${prop.get('price', 'N/A')}\nBeds: {prop.get('beds', 'N/A')}\nBaths: {prop.get('baths', 'N/A')}",
#             }

#             # Conditionally add 'mediaUrl' if it exists
#             media_url = prop.get("image_url") or prop.get("media_url")  # Adjust based on actual data
#             if media_url:
#                 item["mediaUrl"] = media_url
#             else:
#                 logger.warning(f"Property ID {prop.get('id')} is missing 'image_url'.")

#             # Conditionally add 'cards' if 'listingUrl' exists and is valid
#             listing_url = prop.get("listingUrl")
#             if listing_url and listing_url != "#":
#                 item["cards"] = [{
#                     "type": "open_url",
#                     "url": listing_url,
#                     "label": "View Listing"
#                 }]
#             else:
#                 logger.warning(f"Property ID {prop.get('id')} is missing 'listingUrl' or it is invalid.")

#             carousel_items.append(item)

#         # **Debug Log: Print carousel_items**
#         logger.debug(f"Carousel Items: {carousel_items}")

#         if not carousel_items:
#             logger.error("No carousel items to send after processing properties.")
#             return jsonify({'error': 'No valid carousel items to send.'}), 500

#         # Step 9: Prepare Carousel Payload for Pinnacle API
#         carousel_payload = {
#             "from": "test",  # Use 'test' for sending from the Pinnacle test agent
#             "to": phone_number,
#             "cards": carousel_items,  # Assuming 'cards' is the correct field for carousel
#             "text": "Here are some properties that match your search:"
#         }

#         # **Debug Log: Print carousel_payload**
#         logger.debug(f"Carousel Payload: {carousel_payload}")

#         # Step 10: Send Carousel via Pinnacle API
#         headers = {
#             "PINNACLE-API-Key": PINNACLE_API_KEY,  # As per API documentation
#             "Content-Type": "application/json"
#         }

#         response = requests.post(PINNACLE_API_URL, json=carousel_payload, headers=headers)

#         if response.status_code == 200:
#             logger.info(f"Carousel sent successfully to {phone_number}. Response: {response.json()}")
#             return jsonify({'message': 'Carousel sent successfully.'}), 200
#         else:
#             logger.error(f"Failed to send carousel. Status Code: {response.status_code}, Response: {response.text}")
#             return jsonify({'error': 'Failed to send carousel.'}), 500

#     except Exception as e:
#         logger.exception(f"Unhandled exception in /api/send_carousel: {e}")
#         return jsonify({'error': 'Internal server error.'}), 500
