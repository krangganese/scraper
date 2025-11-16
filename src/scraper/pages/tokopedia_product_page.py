from .base_page import BasePage
from selenium.webdriver.common.by import By
from scraper.utils import get_logger
from scraper.config import RAW_DATA_DIR
from pathlib import Path
from urllib.parse import urlparse
import os

logger = get_logger(__name__)


class TokopediaProductPage(BasePage):
    """Page object for Tokopedia product pages"""

    MEDIA_GALLERY_BUTTON_XPATH = '//button[@popovertarget="preview-image"]'
    MEDIA_GALLERY_MODAL_XPATH = (
        "//article[@role='dialog' and @aria-modal='true' and @data-unify='Modal']"
    )

    def __init__(self, driver):
        super().__init__(driver)

    def close_mobile_download_prompt(self):
        """Close the mobile download prompt if it appears."""
        try:
            close_button = self.find_element(
                By.XPATH,
                "//article[@role='dialog' and @aria-labelledby='unf-modal-title' and @data-unify='Modal']//button",
                timeout=15,
            )

            if close_button:
                close_button.click()
                logger.info("Closed mobile download prompt")
                return True

            logger.info("No mobile download prompt to close")
            return False

        except Exception as e:
            logger.error(f"Failed to close mobile download prompt: {str(e)}")
            return False

    def open_media_gallery(self):
        """Open the media gallery on the product page."""
        try:
            gallery_button = self.find_element(
                By.XPATH, self.MEDIA_GALLERY_BUTTON_XPATH, timeout=5
            )

            if not gallery_button:
                logger.error("Media gallery button not found")
                return False

            gallery_button.click()

            modal_element = self.find_element(
                By.XPATH, self.MEDIA_GALLERY_MODAL_XPATH, timeout=5
            )

            if not modal_element:
                logger.error("Media gallery modal did not open correctly")
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to open media gallery: {str(e)}")
            return False

    def save_product_media(self):
        """Extract product media (images/videos) from the product page."""
        save_dir = self.generate_save_dir()

        # Ensure save directory exists
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        result = []
        modal_element = self.find_element(
            By.XPATH, self.MEDIA_GALLERY_MODAL_XPATH, timeout=15
        )

        if not modal_element:
            logger.error("Media gallery modal not found")
            return []

        media_index = 0

        while True:
            # Wait for image to load
            self.random_delay(1.0, 1.5)

            media_element = modal_element.find_element(
                By.XPATH, './/img[@data-testid="PDPImageDetail"]'
            )

            if not media_element:
                logger.error("No media element found")
                break

            media_src = media_element.get_attribute("src")

            if media_src and media_src not in result:
                result.append(media_src)

                # Generate filename with index and proper extension
                filename = self.get_media_name(media_src, index=media_index)
                filepath = save_path / filename

                try:
                    # Take screenshot
                    media_element.screenshot(str(filepath))
                    logger.info(f"Saved media to: {filepath}")
                    media_index += 1
                except Exception as e:
                    logger.error(f"Failed to save screenshot: {str(e)}")

            # Find and click next button
            next_button = self.find_element(
                By.XPATH,
                f'{self.MEDIA_GALLERY_MODAL_XPATH}//button[@type="button" and @data-testid="btnPDPImageDetailNext"]',
                timeout=5,
            )

            if next_button and next_button.is_enabled():
                next_button.click()
                self.random_delay(0.5, 1.0)  # Wait for next image to load
            else:
                logger.info("No more images to process")
                break

        logger.info(f"Total media saved: {len(result)}")
        return result

    def generate_save_dir(self):
        """Generate a directory path to save product media"""
        result = Path(RAW_DATA_DIR) / "tokopedia_product_media"
        result.mkdir(parents=True, exist_ok=True)
        return str(result)

    def get_media_name(self, url: str, index: int = 0):
        """Generate a media filename from its URL"""
        parsed = urlparse(url)
        basename = os.path.basename(parsed.path)

        # If no extension, add .png (common for screenshots)
        if not os.path.splitext(basename)[1]:
            basename = f"product_image_{index}.png"
        # If filename is too generic, add index
        elif basename in ["image", "photo", "product"]:
            name, ext = os.path.splitext(basename)
            basename = f"{name}_{index}{ext}"

        return basename
