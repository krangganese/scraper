from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).parent.parent

# Browser settings
BROWSER = os.getenv("BROWSER", "chrome")
BROWSER_HEADLESS_MODE = os.getenv("BROWSER_HEADLESS_MODE", "false").lower() == "true"
BROWSER_IMPLICIT_WAIT = int(os.getenv("BROWSER_IMPLICIT_WAIT", "10"))
BROWSER_LOAD_TIMEOUT = int(os.getenv("BROWSER_LOAD_TIMEOUT", "30"))

# Window settings
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Retry settings
RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
RETRY_DELAY = 5

# Data directories
DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
INPUTS_DIR = DATA_DIR / "inputs"

# Anti-Bot settings
MIN_DELAY = float(os.getenv("MIN_DELAY", "3"))
MAX_DELAY = float(os.getenv("MAX_DELAY", "5"))

# Logs
LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")
LOG_FILE = LOG_DIR / "scraper.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Export Settings
EXPORT_FORMAT = os.getenv("EXPORT_FORMAT", "csv")  # csv, json, xlsx

# Concurrent Settings
CONCURRENT_SCRAPERS = int(os.getenv("CONCURRENT_SCRAPERS", "1"))

# Application Settings
VERSION = "v2025.0.0"

# Ensure directories exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, LOG_DIR, INPUTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
