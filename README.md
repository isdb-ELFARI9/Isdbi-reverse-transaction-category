# FAS Analysis System

A sophisticated system for analyzing financial transactions and determining their applicability to Financial Accounting Standards (FAS). This system uses a multi-step process to deconstruct transactions, retrieve relevant FAS documents, summarize findings, and analyze applicability.

## Features

- **Transaction Deconstruction**: Breaks down financial transactions into key components
- **FAS Document Retrieval**: Searches across multiple FAS namespaces for relevant standards
- **Intelligent Summarization**: Provides concise summaries of relevant FAS documents
- **Applicability Analysis**: Determines the probability of FAS applicability with detailed reasoning
- **Step-by-Step Processing**: Tracks each step of the analysis process with detailed results

## Project Structure

```
src/
├── api/                    # API layer and endpoints
│   ├── main.py            # FastAPI application setup
│   ├── endpoints.py       # API route definitions
│   └── models.py          # Pydantic data models
├── agents/                # Core business logic components
│   ├── orchestrator.py    # Main orchestration logic
│   ├── transaction_deconstructor.py    # Transaction analysis
│   ├── fas_retriever.py   # FAS document retrieval
│   ├── retrieval_summarizer.py         # Document summarization
│   └── fas_applicability.py            # FAS applicability analysis
└── utils/                 # Utility functions
    └── text_processing.py # Text processing helpers
```

## Setup

1. Clone the repository:

```bash
git clone [repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the server:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```
