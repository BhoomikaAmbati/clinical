import hashlib
import json
import re
from typing import Dict, Any, List, Optional
from preprocessing.schema_inspector import SchemaInspector
from preprocessing.schema_adapter import SchemaAdapter

class ChunkNormalizer:
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Removes extra whitespaces, newlines, and tabs."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def lowercase_normalization(text: str) -> str:
        """Lowercases text where appropriate."""
        if not text:
            return ""
        return text.lower()

    @staticmethod
    def remove_duplicates(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes chunks that have exactly the same text."""
        seen_texts = set()
        unique_chunks = []
        for chunk in chunks:
            text = chunk.get("text", "")
            if text not in seen_texts:
                seen_texts.add(text)
                unique_chunks.append(chunk)
        return unique_chunks

    @staticmethod
    def remove_empty_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes chunks that have empty text."""
        return [chunk for chunk in chunks if chunk.get("text", "").strip()]

class DocumentChunker:
    def __init__(self, min_chunk_size: int = 50, max_chunk_size: int = 1000):
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

    def _generate_chunk_id(self, drug: str, section: str, text: str) -> str:
        """Generates a deterministic SHA-256 ID based on drug, section, and text."""
        unique_string = f"{drug}_{section}_{text}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

    def _extract_drug_name(self, filename: str) -> str:
        """Extracts the drug name from the filename."""
        # e.g. "actemra_v53_2025.json" -> "actemra"
        name = filename.split("_")[0]
        # In case it has no underscores, remove the extension
        if "." in name:
            name = name.split(".")[0]
        return name

    def _split_text(self, text: str) -> List[str]:
        """Splits long text intelligently by sentences or paragraphs if it exceeds max_chunk_size."""
        if len(text) <= self.max_chunk_size:
            return [text]

        # Very basic sentence splitting on period, exclamation, question mark followed by space
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.max_chunk_size:
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        # If a single sentence is still larger than max_chunk_size, split by chunks of max_chunk_size
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > self.max_chunk_size:
                for i in range(0, len(chunk), self.max_chunk_size):
                    final_chunks.append(chunk[i:i+self.max_chunk_size])
            else:
                final_chunks.append(chunk)

        return final_chunks

    def _traverse(self, data: Any, current_path: List[str], extracted: List[Dict[str, str]]):
        """Recursively traverses the JSON structure to extract text and section paths."""
        if isinstance(data, dict):
            for key, value in data.items():
                self._traverse(value, current_path + [str(key)], extracted)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                # For lists we don't necessarily want to append indices to the path
                # unless they have nested dicts, but it can be useful for debugging.
                # However, for section names, we might just use the parent key.
                self._traverse(item, current_path, extracted)
        elif isinstance(data, str):
            text = ChunkNormalizer.normalize_whitespace(data)
            text = ChunkNormalizer.lowercase_normalization(text)
            if text:
                extracted.append({
                    "section": " > ".join(current_path) if current_path else "root",
                    "text": text
                })
        # Ignore other types like int, bool, None

    def chunk_document(self, filename: str, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a filename and a loaded JSON document, returns a list of chunks matching the schema.
        Now uses SchemaInspector and SchemaAdapter for adaptive processing.
        """
        drug_name = self._extract_drug_name(filename)

        # 1. Inspect schema
        inspector = SchemaInspector()
        schema_summary = inspector.inspect(document)
        # Note: the summary can be logged or returned if needed. We'll use it to inform the pipeline conceptually,
        # but the adapter does the actual data transformation.

        # 2. Adapt schema
        adapter = SchemaAdapter()
        adapted_document = adapter.adapt(drug_name, document)

        # We need to traverse the adapted structure. It stores the content in adapted_document["content"]
        extracted_sections = []
        # We traverse original document for backward compatibility of extracted texts
        # But we will use adapted metadata.
        self._traverse(document, [], extracted_sections)

        raw_chunks = []
        for item in extracted_sections:
            section = item["section"]
            text = item["text"]

            # Split text if it's too large
            text_splits = self._split_text(text)

            for split_text in text_splits:
                # Discard extremely small chunks only if it was split
                if len(text_splits) > 1 and len(split_text) < self.min_chunk_size:
                    continue

                chunk_id = self._generate_chunk_id(drug_name, section, split_text)
                raw_chunks.append({
                    "chunk_id": chunk_id,
                    "drug": drug_name,
                    "source_file": filename,
                    "section": section,
                    "text": split_text,
                    "metadata": adapted_document.get("metadata", {
                        "dosage": None,
                        "route": None,
                        "population": None,
                        "warnings": None,
                        "j_codes": None,
                        "black_box": None
                    })
                })

        # Apply normalizations
        normalized_chunks = ChunkNormalizer.remove_empty_chunks(raw_chunks)
        unique_chunks = ChunkNormalizer.remove_duplicates(normalized_chunks)

        return unique_chunks
