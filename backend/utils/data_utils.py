# backend/utils/data_utils.py

import os
import pandas as pd

def load_zillow_data(file_path='data/Zillow_Data.csv') -> pd.DataFrame:
    """
    Load and preprocess Zillow property data from CSV.

    Parameters:
    - file_path (str): Path to the Zillow data CSV file.

    Returns:
    - pd.DataFrame: Preprocessed Zillow data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at path: {file_path}")

    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Drop 'crawl_url_result' if present
    if 'crawl_url_result' in df.columns:
        df = df.drop(columns=['crawl_url_result'])

    # Convert 'price' to numeric
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'].astype(str).str.replace(',', ''), errors='coerce')
    else:
        pass  # Optionally log a warning

    # Convert 'beds' and 'baths' to numeric
    if 'beds' in df.columns:
        df['beds'] = pd.to_numeric(df['beds'], errors='coerce')
    else:
        pass  # Optionally log a warning

    if 'baths' in df.columns:
        df['baths'] = pd.to_numeric(df['baths'], errors='coerce')
    else:
        pass  # Optionally log a warning

    # Convert 'city' and 'state' to title and upper case for consistent matching
    if 'city' in df.columns:
        df['city'] = df['city'].str.title()
    else:
        pass  # Optionally log a warning

    if 'state' in df.columns:
        df['state'] = df['state'].str.upper()
    else:
        pass  # Optionally log a warning

    # Ensure 'zip_code' is string
    if 'zip_code' in df.columns:
        df['zip_code'] = df['zip_code'].astype(str)
    else:
        pass  # Optionally log a warning

    return df

def load_broker_data(file_path='data/broker_data.csv') -> pd.DataFrame:
    """
    Load and preprocess broker data from CSV.

    Parameters:
    - file_path (str): Path to the broker data CSV file.

    Returns:
    - pd.DataFrame: Preprocessed broker data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at path: {file_path}")

    df = pd.read_csv(file_path)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Convert 'zip_code' to string to preserve leading zeros
    if 'zip_code' in df.columns:
        df['zip_code'] = df['zip_code'].astype(str)
    else:
        pass  # Optionally log a warning

    # Convert 'city' and 'state' to title and upper case for consistent matching
    if 'city' in df.columns:
        df['city'] = df['city'].str.title()
    else:
        pass  # Optionally log a warning

    if 'state' in df.columns:
        df['state'] = df['state'].str.upper()
    else:
        pass  # Optionally log a warning

    return df

def get_unique_cities(df: pd.DataFrame) -> list:
    """
    Extract a sorted list of unique cities from the DataFrame.

    Parameters:
    - df (pd.DataFrame): The Zillow data DataFrame.

    Returns:
    - list: Sorted list of unique cities.
    """
    if 'city' in df.columns:
        return sorted(df['city'].dropna().unique())
    else:
        return []
