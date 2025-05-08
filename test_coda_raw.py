import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Get credentials
CODA_API_KEY = os.getenv("CODA_API_KEY")
CODA_DOC_ID = os.getenv("CODA_DOC_ID")

if not CODA_API_KEY or not CODA_DOC_ID:
    print("Error: Missing credentials in .env file")
    exit(1)

# Make the API request
headers = {
    "Authorization": f"Bearer {CODA_API_KEY}",
    "Content-Type": "application/json"
}

url = f"https://coda.io/apis/v1/docs/{CODA_DOC_ID}/tables/grid-vBrJKADk0W/rows"

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes
    
    data = response.json()
    
    # Print first row structure
    if data.get("items") and len(data["items"]) > 0:
        print("\nFirst row structure:")
        print(json.dumps(data["items"][0], indent=2))
    else:
        print("\nNo rows found in the table")
        
except requests.exceptions.RequestException as e:
    print(f"Error making request: {e}")
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}")
except Exception as e:
    print(f"Unexpected error: {e}") 