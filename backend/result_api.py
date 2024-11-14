# backend/result_api.py

from flask import Blueprint, request, jsonify
import logging


from utils import (
    extract_user_intent,
    extract_traits,
    generate_sql_query,
    execute_sql_query,
    sanitize_data,
    extract_feature_from_trait,
    is_trait_matched
)

result_api = Blueprint('result_api', __name__)
logger = logging.getLogger(__name__)

@result_api.route('/api/search_results', methods=['POST'])
def search_results():
    """
    API endpoint that returns search results with 'yes'/'no' indicators.
    Expects a JSON payload with a 'query' field.
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

        # Step 3: Generate SQL Query
        sql_query = generate_sql_query(user_intent, traits, [], query)
        if not sql_query:
            return jsonify({'error': 'Failed to generate SQL query.'}), 500

        # Step 4: Execute SQL Query
        result = execute_sql_query(sql_query)
        if result is None:
            return jsonify({'error': 'Failed to execute SQL query.'}), 500

        # Step 5: Handle Dynamic Columns with Yes/No Indicators
        if result:
            for trait in traits:
                column_name = extract_feature_from_trait(trait)
                for record in result:
                    match_status = is_trait_matched(record, trait)
                    # Assign 'yes' or 'no'
                    if match_status == 'yes':
                        record[column_name] = "yes"
                    elif match_status == 'no':
                        record[column_name] = "no"
                    else:
                        record[column_name] = "no"  # Default to 'no' if unsure
        else:
            logger.info("No results to process for dynamic columns.")

        # Step 6: Sanitize Data
        sanitized_result = sanitize_data(result)

        # Step 7: Compile Response
        response = {
            # 'query': query,
            # 'user_intent': user_intent,
            # 'traits': traits,
            # 'sql_query': sql_query,
            'result': sanitized_result
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Unhandled exception in /api/search_results: {e}")
        return jsonify({'error': 'Internal server error.'}), 500
