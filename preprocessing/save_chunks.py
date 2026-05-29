import json
import os
from pathlib import Path
from typing import List, Dict, Any

from core_config import BASE_DIR

CHUNKS_DIR = BASE_DIR / "chunked"

def create_output_directory():
    """Creates the output directory for chunks if it doesn't exist."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

def save_chunks(drug_name: str, chunks: List[Dict[str, Any]]):
    """
    Saves the list of chunk dictionaries to a JSON file.
    Creates one file per PI source.
    """
    create_output_directory()

    # E.g., actemra_chunks.json
    filename = f"{drug_name}_chunks.json"
    file_path = CHUNKS_DIR / filename

    with file_path.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4, ensure_ascii=False)

    return file_path
