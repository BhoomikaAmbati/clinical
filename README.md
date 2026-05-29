# Clinical Note Pipeline System

## Problem Statement
Healthcare professionals often spend a significant amount of time parsing unstructured clinical notes to extract critical patient information, compare it against established Product Information (PI) for medications, and determine the safest, most effective treatment routes. Doing this manually is time-consuming and error-prone.

## Objective
This project provides a fully localized, container-free automated pipeline to ingest clinical notes, intelligently extract clinical entities (e.g. drugs, symptoms, demographics), retrieve corresponding safety and dosage evidence from PI documents, rank the retrieved evidence based on confidence, and produce a structured, verifiable JSON output alongside automated safety logic inferences.

## System Architecture
The system consists of three main pipelines:
1. **Preprocessing Pipeline**: Loads raw PI JSON files, adapts to unknown schemas, chunks the text, and stores them.
2. **Retrieval Pipeline**: Uses a hybrid lexical (BM25) and semantic (FAISS + MiniLM) approach to find relevant chunks. It then performs Reciprocal Rank Fusion (RRF), reduces duplicates, and routes chunks.
3. **Clinical Pipeline**: Extracts entities from clinical notes, generates query representations, calls the retrieval infrastructure, scores chunks based on metadata matches, reranks them contextually (CrossEncoder), evaluates a final confidence score, aggregates evidence by Product Insert, and applies deterministic safety logic before generating the structured output.

## Workflow
1. PI JSON files are inserted into `data/`.
2. The user invokes index building, which chunks data and stores it in `chunked/`, and then builds `indexes/bm25` and `indexes/faiss`.
3. Clinical notes are submitted via the `api/app.py` FastAPI endpoint.
4. The Clinical Pipeline processes the note, extracts entities, retrieves and ranks evidence, and triggers safety rules (like hospitalization requirements or black box warnings).
5. The API returns the comprehensive structured JSON with `aggregated_evidence`, `safety_decisions`, and `structured_output`.

## Folder Structure
```
├── api/                  # FastAPI layer serving the clinical pipeline
├── chunked/              # Stored JSON chunk outputs from pre-processing
├── clinical/             # Clinical feature extractors, aggregators, safety logic, and output generators
├── config/               # Application configuration and localized settings
├── data/                 # Raw Product Insert JSON files
├── deployment/           # Smoke tests and local environment validators
├── evaluation/           # Performance benchmarking, regression, and metrics
├── indexes/              # Built BM25 and FAISS indexes
├── pipeline/             # Orchestrators bridging preprocessing, retrieval, and clinical tasks
├── preprocessing/        # Chunking and initial document parsers
├── retrieval/            # Hybrid search implementation, fusion, duplicate reduction, and reranking
├── scoring/              # Metadata comparison heuristics and confidence score combinators
└── test_*.py             # Suite of standalone integration tests
```

## Explanation of Every Module
* **`api/`**: Contains FastAPI `app.py` serving HTTP endpoints (`/process_note` and `/rebuild_indexes`).
* **`clinical/entity_extractor.py`**: Deterministic regex-based extractor for identifying age, gender, symptoms, drugs, dosages, etc.
* **`clinical/safety_logic.py`**: Encapsulates regex rules to infer seriousness, hospitalization limits, and black box handling based on extracted info.
* **`clinical/evidence_aggregator.py`**: Groups ranked chunk evidence per original PI source.
* **`config/settings.py`**: Centralized configurations including thresholds, top_k metrics, file paths, model paths, and scoring weights.
* **`deployment/local_setup.py` & `smoke_test.py`**: Scripts to statically validate the directory tree and perform an end-to-end integration smoke test dynamically.
* **`evaluation/metrics.py`**: Information retrieval metrics including Precision@K, Recall@K, NDCG, and MRR.
* **`pipeline/clinical_pipeline.py`**: Orchestrates the entire user note processing lifecycle.
* **`pipeline/ranking_pipeline.py`**: Sub-pipeline focusing specifically on extraction -> generation -> retrieval -> fusion -> scoring.
* **`retrieval/bm25.py` & `retrieval/semantic.py`**: The Lexical and Semantic indexers and searchers.
* **`retrieval/rrf.py` & `retrieval/fusion_pipeline.py`**: Normalizes and fuses retrieval scores, reducing duplicated chunk text.
* **`scoring/metadata_score.py` & `scoring/confidence_score.py`**: Scores specific chunks based on direct matching with extracted clinical features and computes final ranking confidence.

## Setup Instructions
1. Clone the repository to your local machine.
2. Install Python 3.10+ (recommend 3.12).
3. Ensure required directories exist or let the code generate them (`mkdir data chunked indexes/bm25 indexes/faiss`).
4. Install requirements:
   ```bash
   pip install rank_bm25 sentence-transformers faiss-cpu fastapi uvicorn pydantic httpx
   ```

## Local Execution Instructions
### Validation Workflow
You should always run the local validation suite after setting up or modifying code:
```bash
python3 test_evaluation.py
```
This executes local setup validation, smoke tests, regression tests, and benchmarks.

### Rebuild Index Instructions
If you add new PI JSON files into the `data/` folder, you must rebuild the index before querying:
You can trigger the pipeline's internal methods directly:
```python
from retrieval.index_manager import IndexManager
manager = IndexManager()
manager.build_all()
```
Or use the provided API endpoint (if running the server).

## API Usage
Start the server:
```bash
uvicorn api.app:app --host 0.0.0.0 --port 8000
```
**Process a Note**:
```bash
curl -X POST "http://localhost:8000/process_note" -H "Content-Type: application/json" -d '{"note": "Patient presents with severe rheumatoid arthritis. Considering Actemra."}'
```
**Rebuild Indexes**:
```bash
curl -X POST "http://localhost:8000/rebuild_indexes"
```

## Troubleshooting
* **Missing Module Errors**: Ensure all dependencies in the "Setup Instructions" are installed using pip.
* **Empty Retrieval Results**: Ensure that you have rebuilt your indexes (`manager.build_all()`) and that the PI documents were properly formatted JSON files placed inside the `data/` folder.
* **Model Downloading Slow/Failed**: The application uses `sentence-transformers`. It downloads the models locally on the first execution. Ensure you have internet access.

## Limitations
* No graphical UI or front-end interface is provided.
* Currently restricted to purely local inference, with no direct cloud deployment built-in.
* Evaluation relies heavily on rule-based heuristics to establish safety parameters.

## Future Improvements
* Exposing evaluation metrics through continuous integration pipelines.
* Expanding `clinical/safety_logic.py` to leverage LLMs for fuzzy reasoning instead of regex bounds.
* Adding a lightweight UI for medical practitioners.

## Developer Notes
All paths and hyper-parameters are globally exposed via `core_config.py`. Modifying index locations, BM25 constants, or Semantic Model tags must be done inside `config/settings.py`. Ensure you run `pytest` and `test_evaluation.py` before submitting any PRs.