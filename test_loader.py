import sys
import logging
from core_config import DATA_DIR, PI_FILENAMES
from preprocessing.kb_loader import KBLoader

def main():
    print("=== Starting PI Document Loader Test ===\n")

    loader = KBLoader(data_dir=DATA_DIR)

    # Load all files
    try:
        documents = loader.load_all(PI_FILENAMES)
    except Exception as e:
        print(f"Failed to load documents: {e}")
        sys.exit(1)

    print("\n=== Load Summary ===")

    # Print loaded file counts
    successful_loads = {name: doc for name, doc in documents.items() if doc != {}}
    print(f"Total files attempted: {len(PI_FILENAMES)}")
    print(f"Successfully loaded: {len(successful_loads)}")
    print(f"Failed to load: {len(PI_FILENAMES) - len(successful_loads)}\n")

    # Print document sizes
    print("=== Document Sizes (in bytes) ===")
    for filename in PI_FILENAMES:
        doc = documents.get(filename, {})
        if doc == {}:
            print(f"{filename}: Failed to load or empty")
        else:
            # We approximate size by looking at string representation
            size_bytes = len(str(doc).encode('utf-8'))
            print(f"{filename}: {size_bytes} bytes")

    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    main()
