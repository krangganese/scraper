"""
Base scraper class for all scrapers
"""

from abc import ABC, abstractmethod
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from scraper.config import (
    BROWSER,
    BROWSER_HEADLESS_MODE,
    BROWSER_IMPLICIT_WAIT,
    BROWSER_LOAD_TIMEOUT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_DELAY,
    MAX_DELAY,
)
from scraper.utils import get_logger
import time

logger = get_logger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers"""

    def __init__(self, headless=None):
        self.headless = headless if headless is not None else BROWSER_HEADLESS_MODE
        self.driver = None
        self.pipeline = None
        self._page_objects = {}  # Cache for page objects

    def _get_user_agent(self):
        """Get random user agent"""
        user_agents = [
            # List of user agents
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
        ]
        return random.choice(user_agents)

    def _setup_chrome_options(self):
        """Setup Chrome options"""
        options = ChromeOptions()

        # Headless mode
        if self.headless:
            options.add_argument("--headless=new")

        # Window size
        options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")

        # User agent
        options.add_argument(f"user-agent={self._get_user_agent()}")

        # Anti-detection options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Performance options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")

        return options

    def _setup_firefox_options(self):
        """Setup Firefox options"""
        options = FirefoxOptions()

        # Headless mode
        if self.headless:
            options.add_argument("--headless")

        # Window size
        options.add_argument(f"--width={WINDOW_WIDTH}")
        options.add_argument(f"--height={WINDOW_HEIGHT}")

        # User agent
        options.set_preference("general.useragent.override", self._get_user_agent())

        # Anti-detection options
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference("useAutomationExtension", False)

        return options

    def setup_driver(self):
        """Setup the WebDriver based on the selected browser"""
        try:
            if BROWSER.lower() == "chrome":
                options = self._setup_chrome_options()
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            elif BROWSER.lower() == "firefox":
                options = self._setup_firefox_options()
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                raise ValueError(f"Unsupported browser: {BROWSER}")

            # Set timeouts
            self.driver.implicitly_wait(BROWSER_IMPLICIT_WAIT)
            self.driver.set_page_load_timeout(BROWSER_LOAD_TIMEOUT)

            logger.info(f"{BROWSER.capitalize()} WebDriver initialized.")
            return self.driver

        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
            raise

    def navigate_to(self, url):
        """Navigate to a specific URL"""
        try:
            self.driver.get(url)
            logger.info(f"Navigated to URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False

    def is_driver_alive(self):
        """"""
        if not self.driver:
            return False

        try:
            self.driver.current_url
            return True
        except:
            return False

    def reconnect_driver(self):
        """Reconnect the WebDriver"""
        try:
            self.close_driver()
            time.sleep(2)
            self.setup_driver()
            logger.info("WebDriver reconnected.")
            return True
        except Exception as e:
            logger.error(f"Failed to reconnect WebDriver: {str(e)}")
            return False

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed.")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")
            finally:
                self.driver = None
                self._page_objects.clear()

    def close(self):
        """Alias for close_driver to properly close the scraper"""
        self.close_driver()

    def random_delay(self, min_delay=None, max_delay=None):
        """Add random delay to avoid detection"""
        min_d = min_delay if min_delay is not None else MIN_DELAY
        max_d = max_delay if max_delay is not None else MAX_DELAY
        delay = random.uniform(min_d, max_d)
        logger.debug(f"Sleeping for {delay:.2f} seconds")
        time.sleep(delay)
        return delay

    def set_pipeline(self, pipeline):
        """Set the data pipeline"""
        self.pipeline = pipeline
        logger.info(f"Pipeline set: {type(pipeline).__name__}")

    def get_page_object(self, page_class_name):
        """Get or create a page object instance"""
        # Check if page object already exists in cache
        if page_class_name in self._page_objects:
            return self._page_objects[page_class_name]

        # Import and create the page object
        try:
            # Dynamic import based on class name
            if page_class_name == "TokopediaShopPage":
                from scraper.pages.tokopedia_shop_page import TokopediaShopPage

                page_object = TokopediaShopPage(self.driver)
            elif page_class_name == "TokopediaProductPage":
                from scraper.pages.tokopedia_product_page import TokopediaProductPage

                page_object = TokopediaProductPage(self.driver)
            else:
                raise ValueError(f"Unknown page class: {page_class_name}")

            # Cache the page object
            self._page_objects[page_class_name] = page_object
            logger.debug(f"Created page object: {page_class_name}")
            return page_object

        except ImportError as e:
            logger.error(f"Failed to import {page_class_name}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create page object {page_class_name}: {str(e)}")
            raise

    @abstractmethod
    def scrape(self, *args, **kwargs):
        """Abstract method to perform scraping"""
        pass

    def run(self, *args, **kwargs):
        """Run the scraper"""
        try:
            logger.info(f"Starting scraper: {type(self).__name__}")
            self.setup_driver()
            result = self.scrape(*args, **kwargs)
            logger.info(f"Scraper finished: {type(self).__name__}")
            return result
        except Exception as e:
            logger.error(f"Scraper run failed: {str(e)}", exc_info=True)
            raise
        finally:
            self.close_driver()

    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_driver()
