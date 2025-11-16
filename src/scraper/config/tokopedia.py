"""
Config for Tokopedia-related settings
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Tokopedia URLs
TOKOPEDIA_BASE_URL = "https://www.tokopedia.com"
TOKOPEDIA_SEARCH_URL = f"{TOKOPEDIA_BASE_URL}/search"
TOKOPEDIA_SHOP_URL = f"{TOKOPEDIA_BASE_URL}/{{username}}/product"
TOKOPEDIA_LOGIN_URL = f"{TOKOPEDIA_BASE_URL}/login"

# Credentials
TOKOPEDIA_EMAIL = os.getenv("TOKOPEDIA_EMAIL", "")
TOKOPEDIA_PASSWORD = os.getenv("TOKOPEDIA_PASSWORD", "")
