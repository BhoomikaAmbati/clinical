import os
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Known PI filenames
PI_FILENAMES = [
    "actemra_v53_2025.json",
    "lucentis_v27_2025 5.json",
    "ocrevus_v22_2025.json"
]
