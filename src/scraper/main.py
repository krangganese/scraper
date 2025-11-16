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
    VERSION,
)
from scraper.utils import (
    get_logger,
    configure_logging,
    generate_filename,
    export_to_csv,
)
from scraper.scrapers import TokopediaShopScraper, TokopediaProductScraper

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
