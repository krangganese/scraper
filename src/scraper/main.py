"""
Main CLI interface for Scraper
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.config import (
    TOKOPEDIA_SHOP_URL,
    BROWSER_HEADLESS_MODE,
    EXPORTS_DIR,
    INPUTS_DIR,
    VERSION,
)
from scraper.utils import (
    get_logger,
    configure_logging,
    generate_filename,
    export_to_csv,
)
from scraper.scrapers import TokopediaShopScraper, TokopediaProductScraper
import time

logger = get_logger(__name__)


def scrape_image(args):
    """Scrape a single product image"""
    logger.info(f"Scraping product image: {args.product_url}")

    try:
        scraper = TokopediaProductScraper(headless=args.headless)
        scraper.run(args.product_url)
        return True

    except Exception as e:
        logger.error(f"Error scraping product image: {e}")


def scrape_batch(args):
    """Scrape products from a batch of product URLs"""
    logger.info("Scraping batch of product images")

    urls = []
    if args.input_file:
        input_path = Path(args.input_file)

        if not input_path.is_absolute():
            input_path = INPUTS_DIR / input_path

        try:
            with open(input_path, "r") as file:
                urls = [line.strip() for line in file if line.strip()]
            logger.info(f"Loaded {len(urls)} URLs from {input_path}")
        except FileNotFoundError:
            logger.error(f"Input file not found: {input_path}")
            return False
        except Exception as e:
            logger.error(f"Error reading input file {input_path}: {e}")
            return False
    elif args.product_urls:
        urls = args.product_urls
        logger.info(f"Loaded {len(urls)} URLs from command line arguments")
    else:
        logger.error("No input file or product URLs provided for batch scraping")
        return False

    if not urls:
        logger.warning("No URLs. Use --input-file or --product-urls to provide URLs.")
        return False

    logger.info(f"Starting batch scrape for {len(urls)} product URLs")

    scraper = None
    success_count = 0
    failed_urls = []
    try:
        scraper = TokopediaProductScraper(headless=args.headless)
        scraper.setup_driver()

        reconnect_count = 0
        max_reconnects = 3

        for i, url in enumerate(urls, start=1):
            logger.info(f"[{i}/{len(urls)}] Scraping product URL: {url}")

            retry_count = 0
            max_retries = 3
            success = False

            while retry_count < max_retries and not success:
                try:
                    if not scraper.is_driver_alive():
                        if reconnect_count < max_reconnects:
                            scraper.reconnect_driver()
                            reconnect_count += 1
                        else:
                            logger.error("Max WebDriver reconnect attempts reached.")
                            failed_urls.append(url)
                            break

                    result = scraper.run(url)

                    if result:
                        success_count += 1
                        success = True
                        reconnect_count = 0
                    else:
                        retry_count += 1
                        logger.warning(
                            f"Scrape failed for {url}. Retrying ({retry_count}/{max_retries})..."
                        )

                    if i < len(urls):
                        scraper.random_delay(2.0, 4.0)
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to scrape {url}: {e}")

                    if (
                        "Connection refused" in error_msg
                        or "session" in error_msg.lower()
                    ):
                        if scraper.reconnect_driver():
                            reconnect_count += 1
                            retry_count += 1
                            continue
                        else:
                            logger.error("Cannot reconnect. Stopping.")
                            failed_urls.extend(urls[i - 1 :])
                            break

                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(5)

            if not success:
                logger.error(f"Failed to scrape {url} after {max_retries} attempts.")
                failed_urls.append(url)

            if reconnect_count >= max_reconnects:
                logger.error(
                    "Max WebDriver reconnect attempts reached. Stopping batch."
                )
                break

        scraper.close()

        logger.info(
            f"Batch scraping completed: {success_count} succeeded, {len(failed_urls)} failed."
        )

        if failed_urls:
            failed_file = EXPORTS_DIR / generate_filename(
                prefix="failed_urls", extension="txt", timestamp=True
            )
            try:
                with open(failed_file, "w") as f:
                    f.write("\n".join(failed_urls))
                logger.info(f"Failed URLs saved to: {failed_file}")
            except Exception as e:
                logger.error(f"Failed to save failed URLs to file: {e}")
        return success_count > 0

    except Exception as e:
        logger.error(f"Error during batch scraping: {e}")
        if scraper:
            scraper.close()
        return False


def scrape_shop(args):
    """Scrape products from a shop/seller"""
    logger.info(f"Scraping shop: {args.shop_username}")

    try:
        scraper = TokopediaShopScraper(headless=args.headless)

        # Build shop URL
        shop_url = TOKOPEDIA_SHOP_URL.format(username=args.shop_username)
        products = scraper.run(shop_url, page=args.page)

        if not products:
            logger.warning("No products found.")
            return False

        logger.info(f"Scraped {len(products)} products from shop {args.shop_username}")

        if args.filename:
            filename = args.filename
        else:
            filename = generate_filename(
                prefix=f"{args.shop_username}_products",
                extension="csv",
                timestamp=True,
            )

        output_dir = Path(args.output)
        success = export_to_csv(
            data=products,
            output_dir=output_dir,
            filename=filename,
        )

        if success:
            logger.info(f"Data exported successfully to {output_dir / filename}")
            return True
        else:
            logger.error("Failed to export data.")
            return False
    except Exception as e:
        logger.error(f"Error scraping shop: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Tokopedia Shop Scraper CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=BROWSER_HEADLESS_MODE,
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(EXPORTS_DIR),
        help="Output directory for scraped data",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default=None,
        help="Output filename (default: auto-generated with timestamp)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    subparsers = parser.add_subparsers(dest="command", help="Scraping commands")

    # Shop scraper
    shop_parser = subparsers.add_parser("shop", help="Scrape a Tokopedia shop/seller")
    shop_parser.add_argument(
        "--shop-username",
        required=True,
        help="Shop username (e.g., seller-name)",
    )
    shop_parser.add_argument(
        "--sort-by",
        type=str,
        choices=[
            "relevance",
            "latest",
            "lowest_price",
            "highest_price",
            "best_seller",
            "highest_rated",
            "latest_updated",
        ],
        default="relevance",
        help="Sort products by the given option",
    )
    shop_parser.add_argument(
        "--page",
        type=int,
        default=5,
        help="Number of pages to scrape",
    )

    # Product image scraper
    image_parser = subparsers.add_parser(
        "image", help="Scrape product images from a Tokopedia product page"
    )
    image_parser.add_argument(
        "--product-url",
        required=True,
        help="URL of the Tokopedia product page",
    )

    # Batch scraper
    batch_parser = subparsers.add_parser(
        "batch", help="Scrape product images from a batch of products"
    )
    batch_parser.add_argument(
        "--input-file",
        type=str,
        help="Path to input file containing list of shop usernames or product URLs",
    )
    batch_parser.add_argument(
        "--product-urls",
        nargs="+",
        help="List of product URLs to scrape",
    )

    args = parser.parse_args()

    # Set log level
    configure_logging(console_level=args.log_level)

    # Print banner
    print("=" * 60)
    print(f"         TOKOPEDIA SCRAPER {VERSION}")
    print("=" * 60)
    print()

    # Execute command
    if not args.command:
        parser.print_help()
        sys.exit(1)

    success = False

    if args.command == "shop":
        success = scrape_shop(args)
    elif args.command == "image":
        success = scrape_image(args)
    elif args.command == "batch":
        success = scrape_batch(args)

    print()
    print("=" * 60)
    if success:
        print("        SCRAPING COMPLETED SUCCESSFULLY")
    else:
        print("        SCRAPING ENCOUNTERED ERRORS")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
