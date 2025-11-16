"""
Wait utility functions for Selenium WebDriver
"""

import time
import random
from utils import get_logger
from typing import Callable, Any, List

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

logger = get_logger(__name__)


class WaitUtil:
    """Utility class for wait operations"""

    DEFAULT_TIMEOUT = 10
    DEFAULT_POLL_FREQUENCY = 0.5

    @staticmethod
    def wait_for_element(
        driver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT,
        condition: str = "presence",
    ):
        """Wait for an element to be present"""
        try:
            conditions = {
                "presence": EC.presence_of_element_located,
                "visible": EC.visibility_of_element_located,
                "clickable": EC.element_to_be_clickable,
            }

            logger.debug(f"Waiting for element: {by}={value}, condition: {condition}")
            wait_condition = conditions.get(condition, EC.presence_of_element_located)
            element = WebDriverWait(driver, timeout).until(wait_condition((by, value)))
            return element

        except TimeoutException as e:
            logger.error(f"Timeout waiting for element: {by}={value}, Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error waiting for element: {by}={value}, Error: {str(e)}")
            return None

    @staticmethod
    def wait_for_elements(
        driver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT,
        min_elements: int = 1,
        condition: str = "presence",
    ) -> List[Any]:
        """Wait for multiple elements to be present"""
        try:
            conditions = {
                "presence": EC.presence_of_all_elements_located,
                "visible": EC.visibility_of_all_elements_located,
            }

            wait_condition = conditions.get(
                condition, EC.presence_of_all_elements_located
            )
            elements = WebDriverWait(driver, timeout).until(wait_condition((by, value)))

            if len(elements) >= min_elements:
                logger.debug(f"Found {len(elements)} elements for {by}={value}")
                return elements
            else:
                logger.warning(
                    f"Only found {len(elements)} elements for {by}={value}, expected at least {min_elements}"
                )
                return []

        except TimeoutException as e:
            logger.error(f"Timeout waiting for elements: {by}={value}, Error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error waiting for elements: {by}={value}, Error: {str(e)}")
            return []

    @staticmethod
    def wait_for_visible(
        driver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Wait for an element to be visible"""
        return WaitUtil.wait_for_element(
            driver, by, value, timeout, condition="visible"
        )

    @staticmethod
    def wait_for_clickable(
        driver,
        by: str,
        value: str,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """Wait for an element to be clickable"""
        return WaitUtil.wait_for_element(
            driver, by, value, timeout, condition="clickable"
        )

    @staticmethod
    def wait_until(
        driver,
        condition_func: Callable,
        timeout: int = DEFAULT_TIMEOUT,
        poll_frequency: float = DEFAULT_POLL_FREQUENCY,
        error_message: str = "Condition not met within timeout",
    ) -> Any:
        """Wait until a custom condition is met"""
        try:
            result = WebDriverWait(driver, timeout, poll_frequency).until(
                condition_func, message=error_message
            )
            logger.debug("Condition met successfully.")
            return result
        except TimeoutException as e:
            logger.error(f"Timeout waiting for condition: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error waiting for condition: {str(e)}")

    @staticmethod
    def sleep_random(min_seconds: float, max_seconds: float):
        """Sleep for a random duration between min_seconds and max_seconds"""
        duration = random.uniform(min_seconds, max_seconds)
        logger.debug(f"Sleeping for {duration:.2f} seconds")
        time.sleep(duration)

    @staticmethod
    def wait_for_page_load(driver, timeout: int = DEFAULT_TIMEOUT) -> bool:
        """Wait for the page to fully load"""
        try:
            WebDriverWait(driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logger.debug("Page loaded successfully")
            return True
        except TimeoutException:
            logger.warning("Page load timeout")
            return False
        except Exception as e:
            logger.error(f"Error waiting for page load: {str(e)}")
            return False


# Instance functions
def wait_for_element(
    driver,
    by: str,
    value: str,
    timeout: int = WaitUtil.DEFAULT_TIMEOUT,
    condition: str = "presence",
):
    """Wait for an element to be present"""
    return WaitUtil.wait_for_element(driver, by, value, timeout, condition)


def wait_for_elements(
    driver,
    by: str,
    value: str,
    timeout: int = WaitUtil.DEFAULT_TIMEOUT,
    min_elements: int = 1,
    condition: str = "presence",
) -> List[Any]:
    """Wait for multiple elements to be present"""
    return WaitUtil.wait_for_elements(
        driver, by, value, timeout, min_elements, condition
    )


def wait_for_visible(
    driver,
    by: str,
    value: str,
    timeout: int = WaitUtil.DEFAULT_TIMEOUT,
):
    """Wait for an element to be visible"""
    return WaitUtil.wait_for_visible(driver, by, value, timeout)


def wait_for_clickable(
    driver,
    by: str,
    value: str,
    timeout: int = WaitUtil.DEFAULT_TIMEOUT,
):
    """Wait for an element to be clickable"""
    return WaitUtil.wait_for_clickable(driver, by, value, timeout)


def wait_for_page_load(driver, timeout: int = WaitUtil.DEFAULT_TIMEOUT) -> bool:
    """Wait for the page to fully load"""
    return WaitUtil.wait_for_page_load(driver, timeout)
