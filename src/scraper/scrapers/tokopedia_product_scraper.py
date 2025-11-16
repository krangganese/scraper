from .base_scraper import BaseScraper
from scraper.utils import get_logger
from selenium.webdriver.common.by import By

logger = get_logger(__name__)


class TokopediaProductScraper(BaseScraper):
    """Scraper for Tokopedia product pages"""

    def __init__(self, headless=None):
        super().__init__(headless=headless)

    def scrape(self, product_url: str):
        """Scrape the Tokopedia product page for the given product URL."""
        product_page = self.get_page_object("TokopediaProductPage")

        logger.info(f"Navigating to product URL: {product_url}")
        product_page.load(product_url)

        # Close mobile download prompt if it appears
        product_page.close_mobile_download_prompt()

        product_page.open_media_gallery()

        # Extract product media
        media = product_page.save_product_media()

        logger.info(f"Successfully extracted media for product")
        return media

    def run(self, *args, **kwargs):
        """Run the Tokopedia product scraper"""
        logger.info("Starting Tokopedia Product Scraper")
        return super().run(*args, **kwargs)
