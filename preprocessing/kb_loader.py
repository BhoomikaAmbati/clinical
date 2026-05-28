import json
import logging
from pathlib import Path
from typing import Dict, Any, List

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class KBLoader:
    """
    A knowledge base loader class to load clinical PI JSON documents.
    """

    def __init__(self, data_dir: Path):
        """
        Initializes the KBLoader with a data directory.

        Args:
            data_dir (Path): The path to the directory containing JSON files.
        """
        self.data_dir = data_dir

    def load_document(self, filename: str) -> Dict[str, Any]:
        """
        Loads a single JSON document by filename.

        Args:
            filename (str): The name of the file to load (e.g., 'doc.json').

        Returns:
            Dict[str, Any]: The parsed JSON document as a Python dictionary.
                            Returns an empty dictionary if the file doesn't exist
                            or if it contains malformed JSON.
        """
        file_path = self.data_dir / filename

        if not file_path.exists():
            logger.error(f"Missing file: {file_path}")
            return {}

        if not file_path.is_file():
            logger.error(f"Not a regular file: {file_path}")
            return {}

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Successfully loaded: {filename}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {e}")
            return {}

    def load_all(self, filenames: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Loads multiple JSON documents by their filenames.

        Args:
            filenames (List[str]): A list of filenames to load.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary mapping filenames to their parsed JSON content.
        """
        results = {}
        for filename in filenames:
            results[filename] = self.load_document(filename)
        return results
