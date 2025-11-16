from .base_page import BasePage
from scraper.utils import get_logger, scroll_to_bottom

from selenium.webdriver.common.by import By

logger = get_logger(__name__)


class TokopediaShopPage(BasePage):
    """Page object for Tokopedia shop pages"""

    SORT_BY = {
        "relevance": "Paling Sesuai",
        "latest": "Terbaru",
        "lowest_price": "Harga Terendah",
        "highest_price": "Harga Tertinggi",
        "best_seller": "Pembelian Terbanyak",
        "highest_rated": "Ulasan Terbanyak",
        "latest_updated": "Pembaruan Terakhir",
    }
    PRODUCT_CONTAINER_XPATH = (
        '(//h4[@data-testid="showCaseTitle"]/following-sibling::div)[1]/div[1]'
    )

    PRODUCT_PAGINATION_XPATH = (
        '(//h4[@data-testid="showCaseTitle"]/following-sibling::div)[1]/div[2]/ul'
    )
    PRODUCT_CARD_XPATH = './*[name()="div"]'
    PRODUCT_LINK_XPATH = (
        '//a[@data-theme="default" and contains(@href,"tokopedia.com/")]'
    )

    def __init__(self, driver):
        super().__init__(driver)

    def sort_by(self, sort_option: str):
        """Sort products by the given option on the shop page."""
        if sort_option not in self.SORT_BY:
            logger.error(f"Invalid sort option: {sort_option}")
            return

        sort_dropdown_selector = (
            'button[data-unify="Select"][type="button"][aria-haspopup="listbox"]'
        )
        sort_dropdown_dialog_selector = (
            'div[role="dialog"][data-unify="Dropdown"][aria-modal="true"]'
        )

        # Click the sort dropdown
        sort_dropdown = self.find_element(
            By.CSS_SELECTOR, sort_dropdown_selector, timeout=5
        )

        logger.info(f"Sort dropdown element: {sort_dropdown}")

        if not sort_dropdown:
            logger.error("Sort dropdown not found")
            return None

        sort_dropdown.click()

        # Wait for the dropdown dialog to appear
        sort_dropdown_dialog = self.find_element(
            By.CSS_SELECTOR, sort_dropdown_dialog_selector, timeout=5
        )

        if not sort_dropdown_dialog:
            logger.error("Sort dropdown dialog not found")
            return None

        sort_option_selector = f'button[data-unf="select-menu-item-btn"][data-item-text="{self.SORT_BY[sort_option]}"]'
        # Select the desired sort option
        sort_option_element = self.find_element(
            By.CSS_SELECTOR, sort_option_selector, timeout=5
        )

        if not sort_option_element:
            logger.error("Sort option element option not found")
            return None

        sort_option_element.click()

        logger.info(f"Sorted products by: {sort_option}")

    def scroll_until_loaded(self, max_scrolls=5, delay=1.0):
        """Scroll the shop page until all products are loaded or max scrolls reached"""
        last_count = 0
        scroll = 0

        while scroll < max_scrolls:
            container = self.find_element(
                By.XPATH,
                self.PRODUCT_CONTAINER_XPATH,
                timeout=5,
            )

            if not container:
                logger.error("Product container not found during scroll.")
                return

            cards = container.find_elements(By.XPATH, self.PRODUCT_CARD_XPATH)
            current_count = len(cards)

            if current_count == last_count:
                logger.info("No new products loaded after scrolling.")
                break

            last_count = current_count
            scroll += 1

            self.scroll_page_to_bottom()
            self.random_delay(delay, delay + 0.5)

    def get_product_cards(self, page: int = 5):
        """Get product card elements from the shop page and extract their info"""

        result = []

        for current_page in range(1, page + 1):
            logger.info(f"Scraping page {current_page} of {page}")

            product_container = self.find_element(
                By.XPATH,
                self.PRODUCT_CONTAINER_XPATH,
                timeout=15,
            )

            if not product_container:
                logger.error(f"No product container found")
                break

            self.scroll_until_loaded(max_scrolls=3, delay=1.0)

            product_cards = product_container.find_elements(
                By.XPATH, self.PRODUCT_CARD_XPATH
            )

            logger.info(f"Found {len(product_cards)} products on page {current_page}")

            # Extract product info immediately while elements are still valid
            for card in product_cards:
                try:
                    info = self.extract_product_info(card)
                    if info:
                        result.append(info)
                except Exception as e:
                    logger.warning(f"Failed to extract product from card: {str(e)}")
                    continue

            # Navigate to next page if not on the last page
            if current_page < page:
                if not self.next_page():
                    logger.info("No more pages available.")
                    break

        logger.info(f"Total products scraped: {len(result)}")
        return result

    def next_page(self):
        """Navigate to the next page of products"""
        pagination_container = self.find_element(
            By.XPATH,
            self.PRODUCT_PAGINATION_XPATH,
            timeout=5,
        )

        if not pagination_container:
            logger.error("Pagination container not found.")
            return False

        # Scroll to pagination area first
        self.scroll_to(By.XPATH, self.PRODUCT_PAGINATION_XPATH)
        self.random_delay(0.5, 1.0)

        # Use XPath to find the last link that's not disabled
        next_button_xpath = f"{self.PRODUCT_PAGINATION_XPATH}//a[last()]"

        # Check if button exists and is not disabled
        next_button = self.find_element(By.XPATH, next_button_xpath, timeout=5)

        if not next_button:
            logger.info("Next button not found.")
            return False

        if "disabled" in next_button.get_attribute("class"):
            logger.info("No more pages available.")
            return False

        # Use JavaScript click to avoid interception
        try:
            self.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", next_button
            )
            self.random_delay(0.3, 0.5)
            self.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            logger.error(f"Failed to click next button: {str(e)}")
            return False

        # Wait for navigation
        self.wait_for_page_load()
        self.scroll_page_to_top()
        self.random_delay(1.5, 2.5)

        logger.info("Navigated to the next page.")
        return True

    def extract_product_info(self, product_card):
        """Extract product information from a product card element"""
        try:
            # Get the link (most stable selector)
            link_element = product_card.find_element(
                By.XPATH, './/a[@data-theme="default"]'
            )
            product_link = link_element.get_attribute("href")

            # Get product name - it's in a span within the link
            # Using the structure: a > div > div > div > span (the first text span)
            product_name = product_card.find_element(
                By.XPATH,
                './/a[@data-theme="default"]//span[string-length(text()) > 16]',
            ).text.strip()

            # Get product price - look for text starting with "Rp"
            product_price = product_card.find_element(
                By.XPATH, './/div[starts-with(text(), "Rp")]'
            ).text.strip()

            # Get product image - it's the img tag with alt="product-image"
            image_element = product_card.find_element(
                By.XPATH, './/img[@alt="product-image"]'
            )
            # Note: The src might be a placeholder, check for data-src or other attributes
            product_image = image_element.get_attribute(
                "data-src"
            ) or image_element.get_attribute("src")

            return {
                "name": product_name,
                "price": product_price,
                "image": product_image,
                "link": product_link,
            }
        except Exception as e:
            logger.error(f"Failed to extract product info: {str(e)}")
            return None

    def extract_product_link(self, product_card):
        """Extract product link from a product card element"""
        try:
            link_element = product_card.find_element(By.XPATH, self.PRODUCT_LINK_XPATH)
            product_link = link_element.get_attribute("href")
            return product_link
        except Exception as e:
            logger.error(f"Failed to extract product link: {str(e)}")
            return None
