# config.py
import os
from dotenv import load_dotenv

def get_api_key():
    """
    Loads the Google API key from the .env file.
    """
    load_dotenv() # Load environment variables from .env file
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")
    return api_key

if __name__ == "__main__":
    # Example usage and basic test
    try:
        key = get_api_key()
        print(f"API Key loaded successfully (first 5 chars): {key[:5]}...")
    except ValueError as e:
        print(f"Error: {e}")
