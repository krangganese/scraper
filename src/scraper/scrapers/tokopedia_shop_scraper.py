from .base_scraper import BaseScraper
from scraper.utils import get_logger
from selenium.webdriver.common.by import By

logger = get_logger(__name__)


class TokopediaShopScraper(BaseScraper):
    """Scraper for Tokopedia shop pages"""

    def __init__(self, headless=None):
        super().__init__(headless=headless)

    def scrape(self, shop_url: str, page: int = 5):
        """Scrape the Tokopedia shop page for the given shop username."""
        shop_page = self.get_page_object("TokopediaShopPage")

        logger.info(f"Navigating to shop URL: {shop_url}")
        shop_page.load(shop_url)

        # Extract product data - get_product_cards now returns extracted info
        products = shop_page.get_product_cards(page=page)

        # Filter out None values
        result = [p for p in products if p is not None]

        logger.info(f"Successfully extracted {len(result)} products")
        return result

    def run(self, *args, **kwargs):
        """Run the Tokopedia shop scraper"""
        logger.info("Starting Tokopedia Shop Scraper")
        return super().run(*args, **kwargs)
