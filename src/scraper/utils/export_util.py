import csv
import json
from pathlib import Path
from datetime import datetime
from scraper.utils import get_logger

logger = get_logger(__name__)


def export_to_csv(data, output_dir, filename=None, quote_type='"'):
    """Export data to a CSV file"""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            filename = generate_filename(prefix="scraped_data", extension="csv")

        output_path = output_dir / filename

        if not data:
            logger.warning("No data to export to CSV.")
            return None

        keys = data[0].keys()
        with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=keys, quotechar='"', quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            writer.writerows(data)

        logger.info(f"Data exported to CSV: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to export data to CSV: {str(e)}")
        return None


def export_to_json(data, output_dir, filename=None):
    """Export data to a JSON file"""
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            filename = generate_filename(prefix="scraped_data", extension="json")

        output_path = output_dir / filename

        with open(output_path, mode="w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, ensure_ascii=False, indent=4)

        logger.info(f"Data exported to JSON: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to export data to JSON: {str(e)}")
        return None


def generate_filename(prefix="scraped_data", extension="csv", timestamp=True):
    """Generate a filename with timestamp"""
    if not timestamp:
        return f"{prefix}.{extension}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"
