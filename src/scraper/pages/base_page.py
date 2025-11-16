"""
Base page object with common methods for all pages
"""

import time
import random
from scraper.config import BROWSER_IMPLICIT_WAIT, MIN_DELAY, MAX_DELAY
from scraper.utils import (
    get_logger,
    scroll_to_element,
    scroll_page,
    wait_for_element,
    wait_for_elements,
)

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = get_logger(__name__)


class BasePage:
    """Base class for all page objects"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, BROWSER_IMPLICIT_WAIT)

    def load(self, url):
        """Navigate to a URL and wait for page to load"""
        try:
            logger.info(f"Loading page: {url}")
            self.driver.get(url)
            self.wait_for_page_load()
            self.random_delay()
            logger.info(f"Page loaded successfully: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to load page {url}: {str(e)}")
            return False

    def find_element(self, by, value, timeout=None):
        """Find a single element with error handling"""
        return wait_for_element(self.driver, by, value, timeout)

    def find_elements(self, by, value, timeout=None):
        """Find multiple elements with error handling"""
        return wait_for_elements(self.driver, by, value, timeout)

    def click_element(self, by, value, timeout=None):
        try:
            element = self.find_element(by, value, timeout)
            if element:
                self.wait.until(EC.element_to_be_clickable((by, value)))
                element.click()
                logger.debug(f"Clicked element: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to click element: {by}={value}, Error: {str(e)}")
            return False

    def input_text(self, by, value, text, clear=True):
        """Input text into an element"""
        try:
            element = self.find_element(by, value)
            if element:
                if clear:
                    element.clear()
                element.send_keys(text)
                logger.debug(f"Input txt into element: {by}={value}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to input text: {by}={value}, Error: {str(e)}")
            return False

    def get_text(self, by, value, timeout=None):
        """Get text from an element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                return element.text.strip()
            return ""
        except Exception as e:
            logger.error(f"Failed to get text: {by}={value}, Error: {str(e)}")
            return ""

    def get_attribute(self, by, value, attribute, timeout=None):
        """Get attribute value from an element"""
        try:
            element = self.find_element(by, value, timeout)
            if element:
                return element.get_attribute(attribute)
            return None
        except Exception as e:
            logger.error(f"Failed to get attribute: {by}={value}, Error: {str(e)}")
            return None

    def is_element_visible(self, by, value, timeout=5):
        """Check if element is visible"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def scroll_to(self, by, value):
        """Scroll to an element"""
        try:
            element = self.find_element(by, value)
            if element:
                scroll_to_element(self.driver, element)
                self.random_delay(0.5, 1.5)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to scroll to element: {by}={value}, Error: {str(e)}")
            return False

    def scroll_page_down(self, scrolls=3):
        """Scroll page down multiple times"""
        scroll_page(self.driver, direction="down", scrolls=scrolls)
        self.random_delay()

    def scroll_page_to_top(self):
        """Scroll to top of page"""
        scroll_page(self.driver, direction="top")
        self.random_delay()

    def scroll_page_to_bottom(self):
        """Scroll to bottom of page"""
        scroll_page(self.driver, direction="bottom")
        self.random_delay()

    def wait_for_page_load(self, timeout=30):
        """Wait for page to fully load"""
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.debug("Page loaded successfully")
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False

    def random_delay(self, min_delay=None, max_delay=None):
        """Add random delay to simulate human behavior"""
        min_d = min_delay if min_delay is not None else MIN_DELAY
        max_d = max_delay if max_delay is not None else MAX_DELAY
        delay = random.uniform(min_d, max_d)
        logger.debug(f"Waiting for {delay:.2f} seconds")
        time.sleep(delay)

    def execute_script(self, script, *args):
        """Execute JavaScript"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            logger.error(f"Failed to execute script: {str(e)}")
            return None

    def take_screenshot(self, filename):
        """Take screenshot"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return False

    def get_current_url(self):
        """Get current URL"""
        return self.driver.current_url

    def refresh_page(self):
        """Refresh current page"""
        self.driver.refresh()
        self.wait_for_page_load()
        logger.debug("Page refreshed")

    def go_back(self):
        """Navigate back"""
        self.driver.back()
        self.wait_for_page_load()
        logger.debug("Navigated back")

    def close_page(self):
        """Close current page/tab"""
        self.driver.close()

    def quit(self):
        """Quit driver"""
        self.driver.quit()
        logger.info("Driver closed")
