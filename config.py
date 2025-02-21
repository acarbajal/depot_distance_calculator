# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
MAPQUEST_API_KEY = os.getenv('MAPQUEST_API_KEY')

# Validate that required environment variables are set
if not MAPQUEST_API_KEY:
    raise ValueError("MAPQUEST_API_KEY environment variable is not set")

if not GOOGLE_MAPS_API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set")


INPUT_SHEET_NAME = "Depots"
OUTPUT_SHEET_NAME = "Driving Times"
REQUIRED_COLUMNS = ["Depot Designation", "Depot Address"]
