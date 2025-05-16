# FAS Retriever Documentation

## Overview

The FAS Retriever is a specialized agent designed to retrieve relevant sections from FAS (Financial Accounting Standards) documents based on semantic queries. It uses vector embeddings and Pinecone for efficient document retrieval.

## Data Structures

### FASDocument Model

```python
class FASDocument(BaseModel):
    id: str                    # Unique identifier for the document chunk
    text: str                  # The actual text content
    relevance_score: float     # Similarity score (0-1)
    document_type: str         # Type of FAS document (e.g., "FAS_32")
    section_heading: str       # Section title/heading
    source_filename: str       # Original source file name
    chunk_index: int          # Position in the chunked document
    total_chunks: int         # Total number of chunks in the document
    metadata: Optional[Dict]  # Additional metadata
```

## Key Methods

### 1. `__init__()`

Initializes the FAS Retriever with Pinecone connection.

- **Input**: None
- **Output**: None
- **Side Effects**:
  - Establishes connection to Pinecone
  - Verifies index connection
  - Sets up OpenAI client

### 2. `embed_query(query: str) -> list`

Converts a text query into a vector embedding.

- **Input**:
  - `query`: String containing the search query
- **Output**:
  - List of floats representing the query embedding
- **Used Model**: OpenAI's text-embedding-3-small

### 3. `retrieve(query: str, top_n: int = 5, document_types: Optional[Union[str, List[str]]] = None, section_heading: Optional[str] = None, namespace: str = "default") -> List[FASDocument]`

Main method for retrieving relevant documents.

- **Input**:
  - `query`: Search query string
  - `top_n`: Number of results to return (default: 5)
  - `document_types`: Optional filter for specific FAS types
  - `section_heading`: Optional filter for specific sections
  - `namespace`: Pinecone namespace (default: "default")
- **Output**: List of FASDocument objects
- **Process**:
  1. Embeds the query
  2. Applies filters if specified
  3. Searches Pinecone index
  4. Formats results into FASDocument objects

### 4. `retrieve_by_keywords(keywords: List[str], top_n: int = 5, document_types: Optional[Union[str, List[str]]] = None, section_heading: Optional[str] = None, namespace: str = "default") -> List[FASDocument]`

Retrieves documents using a list of keywords.

- **Input**:
  - `keywords`: List of search terms
  - Other parameters same as `retrieve()`
- **Output**: List of FASDocument objects
- **Process**: Joins keywords and calls `retrieve()`

### 5. `get_available_document_types() -> List[str]`

Returns list of supported FAS document types.

- **Input**: None
- **Output**: List of available FAS document types

## Filter Examples

### Document Type Filter

```python
# Single document type
filter_criteria = {"document_type": {"$eq": "FAS_32"}}

# Multiple document types
filter_criteria = {"document_type": {"$in": ["FAS_32", "FAS_28"]}}
```

### Section Heading Filter

```python
filter_criteria = {"section_heading": {"$eq": "Operating Ijarah"}}
```

### Combined Filters

```python
filter_criteria = {
    "$and": [
        {"document_type": {"$eq": "FAS_32"}},
        {"section_heading": {"$eq": "Operating Ijarah"}}
    ]
}
```

## Error Handling

- Connection errors to Pinecone are caught and logged
- Empty results return an empty list
- Invalid filters are handled gracefully

## Dependencies

- OpenAI API (for embeddings)
- Pinecone (for vector storage)
- Pydantic (for data validation)
