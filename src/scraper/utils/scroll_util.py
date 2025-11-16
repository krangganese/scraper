"""
Scroll utility module for Selenium WebDriver
"""

import time
from typing import Tuple
from scraper.utils import get_logger
from selenium.webdriver.remote.webelement import WebElement

logger = get_logger(__name__)


class ScrollUtil:
    """
    Utility class for Selenium WebDriver scroll operation
    """

    DEFAULT_SCROLL_DELAY = 1.0
    DEFAULT_SCROLL_PAUSE = 0.5

    @staticmethod
    def scroll_to_element(
        driver, element: WebElement, align_to_top: bool = True, behavior: str = "smooth"
    ):
        """Scroll into a specific element"""
        try:
            # Use scrollIntoView for better compatibility
            script = f"""
            arguments[0].scrollIntoView({{
                behavior: '{behavior}',
                block: '{'start' if align_to_top else 'end'}'
            }});
            """
            driver.execute_script(script, element)
            logger.debug("Scrolled to element successfully.")
            time.sleep(ScrollUtil.DEFAULT_SCROLL_PAUSE)
            return True
        except Exception as e:
            logger.error(f"Error scrolling to element: {str(e)}")
            return False

    @staticmethod
    def scroll_to_bottom(driver, smooth: bool = True) -> bool:
        """Scroll to the bottom of the page"""
        try:
            if smooth:
                script = """
                window.scrollTo({
                    top: document.body.scrollHeight,
                    behavior: 'smooth'
                });
                """
            else:
                script = "window.scrollTo(0, document.body.scrollHeight);"

            driver.execute_script(script)
            logger.debug("Scrolled to bottom")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to scroll to bottom: {str(e)}")
            return False

    @staticmethod
    def scroll_to_top(driver, smooth: bool = True) -> bool:
        """Scroll to the top of the page"""
        try:
            if smooth:
                script = """
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                """
            else:
                script = "window.scrollTo(0, 0);"

            driver.execute_script(script)
            logger.debug("Scrolled to top")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to scroll to top: {str(e)}")
            return False

    @staticmethod
    def scroll_to_coordinate(driver, x: int, y: int, smooth: bool = True) -> bool:
        """Scroll to specific coordinates on the page"""
        try:
            if smooth:
                script = f"""
                window.scrollTo({{
                    top: {y},
                    left: {x},
                    behavior: 'smooth'
                }});
                """
            else:
                script = f"window.scrollTo({x}, {y});"

            driver.execute_script(script)
            logger.debug(f"Scrolled to coordinates ({x}, {y})")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to scroll to coordinates ({x}, {y}): {str(e)}")
            return False

    @staticmethod
    def get_scroll_position(driver) -> Tuple[int, int]:
        """Get the current scroll position"""
        try:
            script = "return [window.pageXOffset, window.pageYOffset];"
            position = driver.execute_script(script)
            logger.debug(f"Current scroll position: {position}")
            return tuple(position)
        except Exception as e:
            logger.error(f"Failed to get scroll position: {str(e)}")
            return (0, 0)

    @staticmethod
    def scroll_page(
        driver,
        direction: str = "down",
        scrolls: int = 1,
        delay: float = DEFAULT_SCROLL_DELAY,
    ) -> bool:
        """Scroll the page up or down by a number of scrolls"""
        try:
            for i in range(scrolls):
                if direction == "down":
                    driver.execute_script("window.scrollBy(0, window.innerHeight);")
                elif direction == "up":
                    driver.execute_script("window.scrollBy(0, -window.innerHeight);")
                elif direction == "bottom":
                    ScrollUtil.scroll_to_bottom(driver, smooth=True)
                elif direction == "top":
                    ScrollUtil.scroll_to_top(driver, smooth=True)
                else:
                    logger.error(f"Invalid scroll direction: {direction}")
                    return False

                if i < scrolls - 1:
                    time.sleep(delay)

            logger.debug(f"Scrolled {direction} {scrolls} times with delay {delay}")
            return True
        except Exception as e:
            logger.error(f"Failed to scroll {direction}: {str(e)}")
            return False


# Instance of ScrollUtil for easy access
def scroll_to_element(
    driver, element: WebElement, align_to_top: bool = True, behavior: str = "smooth"
):
    return ScrollUtil.scroll_to_element(driver, element, align_to_top, behavior)


def scroll_to_bottom(driver, smooth: bool = True) -> bool:
    return ScrollUtil.scroll_to_bottom(driver, smooth)


def scroll_to_top(driver, smooth: bool = True) -> bool:
    return ScrollUtil.scroll_to_top(driver, smooth)


def scroll_page(
    driver,
    direction: str = "down",
    scrolls: int = 1,
    delay: float = ScrollUtil.DEFAULT_SCROLL_DELAY,
) -> bool:
    return ScrollUtil.scroll_page(driver, direction, scrolls, delay)
