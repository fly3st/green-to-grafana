import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_URL = os.getenv("API_URL")

if not API_URL:
    raise ValueError("API URL not found in .env file")

# Check if response is successful and print records
try:
    print("Fetching data from API...")
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Data fetched successfully!\n")

    records = data['result']['records']
    print(f"Total records fetched: {len(records)}\n")

    # Convert to DataFrame and show column names
    df = pd.DataFrame(records)

    print(df.columns.tolist())
    print()

    # Print first 3 rows
    print(df.head(3).to_string(index=False))

except requests.exceptions.HTTPError as e:
    print(f"Failed to fetch data. Status code: {e}")
    print(response.text)
    exit()
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    exit()
except Exception as e:
    print(f"Unexpected error: {e}")
    exit()

