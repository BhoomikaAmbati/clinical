import sys
import json
from collections import Counter
from config import DATA_DIR, PI_FILENAMES
from preprocessing.kb_loader import KBLoader
from preprocessing.chunker import DocumentChunker
from preprocessing.save_chunks import save_chunks

def main():
    print("=== Starting PI Document Chunking Test ===\n")

    loader = KBLoader(data_dir=DATA_DIR)
    chunker = DocumentChunker()

    try:
        documents = loader.load_all(PI_FILENAMES)
    except Exception as e:
        print(f"Failed to load documents: {e}")
        sys.exit(1)

    for filename in PI_FILENAMES:
        doc = documents.get(filename, {})
        if not doc:
            print(f"Skipping {filename}: Failed to load or empty")
            continue

        print(f"Processing {filename}...")

        chunks = chunker.chunk_document(filename, doc)

        if not chunks:
            print(f"No chunks generated for {filename}")
            continue

        # Determine drug name
        drug_name = chunker._extract_drug_name(filename)

        # Save chunks
        saved_path = save_chunks(drug_name, chunks)

        # Summary statistics
        print(f"Total chunks: {len(chunks)}")
        print(f"Saved to: {saved_path}")

        # Section distribution
        sections = [chunk.get("section", "unknown") for chunk in chunks]
        section_counts = Counter(sections)
        print("Section distribution:")
        for section, count in section_counts.most_common(5):
            print(f"  {section}: {count}")

        # Sample chunk
        print("\nSample chunk:")
        print(json.dumps(chunks[0], indent=2))
        print("-" * 40)

    print("\n=== Chunking Test Completed Successfully ===")

if __name__ == "__main__":
    main()
