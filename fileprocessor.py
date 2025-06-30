import csv
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def read_csv_json_file(file_path):
    """
    Reads the content of a CSV or JSON file and returns it as a list of dictionaries.
    
    Args:
        file_path (str): The path to the file to be read.
        
    Returns:
        list: The content of the file.
    """
    file_path = Path(file_path)
            
    if not file_path.exists():
        logger.error(f"❌ File not found: {file_path}")
        return None
    
    content = []
    
    # Read file based on extension
    if file_path.suffix.lower() == '.csv':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                content = [row for row in reader]
        except csv.Error as e:
            logger.error(f"❌ Error reading CSV file: {e}")
            return None
    elif file_path.suffix.lower() == '.json':
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error reading JSON file: {e}")
            return None
    else:
        logger.error(f"❌ Unsupported file format: {file_path.suffix}")
        return None
    return content


def write_csv_json_file(file_path, data):
    """
    Writes a list of dictionaries to a CSV or JSON file.
    
    Args:
        file_path (str): The path to the file to be written.
        data (list): The data to be written to the file.
        
    Returns:
        bool: True if the file was written successfully, False otherwise.
    """
    file_path = Path(file_path)
    
    if not data:
        logger.error("❌ No data provided to write.")
        return False
    
    # Write file based on extension
    if file_path.suffix.lower() == '.csv':
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            logger.error(f"❌ Error writing CSV file: {e}")
            return False
    elif file_path.suffix.lower() == '.json':
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            logger.error(f"❌ Error writing JSON file: {e}")
            return False
    else:
        logger.error(f"❌ Unsupported file format: {file_path.suffix}")
        return False