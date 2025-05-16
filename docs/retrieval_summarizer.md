# Retrieval Summarizer Documentation

## Overview

The Retrieval Summarizer is an agent that processes and summarizes findings from FAS documents retrieved by the FAS Retriever. It uses OpenAI's GPT model to generate comprehensive summaries of the retrieved content.

## Core Logic

### 1. Document Processing Flow

1. Receives FASDocument objects from the retriever
2. Extracts relevant metadata and content
3. Formats information for summarization
4. Generates structured summaries using GPT
5. Organizes summaries by namespace

### 2. Summarization Process

The summarizer follows these steps:

1. **Context Preparation**: Combines document content with metadata
2. **Prompt Engineering**: Creates a structured prompt for GPT
3. **Summary Generation**: Uses GPT to create comprehensive summaries
4. **Result Organization**: Groups summaries by namespace

## Key Methods

### 1. `__init__()`

Initializes the summarizer with OpenAI client.

- **Input**: None
- **Output**: None
- **Side Effects**: Sets up OpenAI client with API key

### 2. `_summarize_fas_findings(documents: List[FASDocument]) -> str`

Internal method for summarizing a list of FAS documents.

- **Input**: List of FASDocument objects
- **Output**: String containing the summary
- **Process**:
  1. Formats document context with metadata
  2. Creates summarization prompt
  3. Calls GPT for summary generation
  4. Returns formatted summary

### 3. `summarize_findings(results_by_namespace: Dict[str, List[FASDocument]]) -> Dict[str, str]`

Main method for summarizing findings across namespaces.

- **Input**: Dictionary mapping namespaces to document lists
- **Output**: Dictionary mapping namespaces to summaries
- **Process**:
  1. Processes each namespace separately
  2. Generates summaries for each namespace
  3. Returns organized summary dictionary

### 4. `print_summaries(summaries: Dict[str, str]) -> None`

Utility method for formatted summary printing.

- **Input**: Dictionary of summaries
- **Output**: None (prints to console)
- **Format**: Structured console output with separators

## Prompts

### 1. System Prompt

```python
"You are a financial accounting expert specializing in Islamic finance and FAS standards.
Provide detailed, accurate summaries that maintain technical precision while being clear and accessible."
```

### 2. Main Summarization Prompt

```python
"""Please analyze the following FAS document excerpts and provide a comprehensive summary of the key findings.
Focus on the most relevant and important information that would be useful for understanding the accounting treatment.

Document excerpts:
{context}

Please provide a clear and structured summary that:
1. Highlights the key accounting principles or requirements
2. Identifies any specific conditions or criteria mentioned
3. Notes any important exceptions or special cases
4. References specific sections and document types where relevant
5. Maintains technical accuracy while being understandable
6. Includes any relevant metadata that provides context

Summary:"""
```

## Context Format

The summarizer formats document context as follows:

```python
f"Document {i+1} (Relevance: {doc.relevance_score:.2f}):\n"
f"Document Type: {doc.document_type}\n"
f"Section: {doc.section_heading}\n"
f"Source: {doc.source_filename}\n"
f"Content:\n{doc.text}"
```

## GPT Parameters

- **Model**: gpt-3.5-turbo
- **Temperature**: 0.2 (for focused, consistent outputs)
- **Max Tokens**: 800 (for detailed summaries)

## Error Handling

- Empty document lists return "No relevant findings found"
- API errors are caught and return "Error generating summary"
- Invalid inputs are handled gracefully

## Dependencies

- OpenAI API (for GPT model)
- FAS Retriever (for document input)
- Pydantic (for data validation)

## Example Usage

```python
# Initialize summarizer
summarizer = RetrievalSummarizer()

# Get documents from retriever
documents = retriever.retrieve("query")

# Generate summaries
summaries = summarizer.summarize_findings({"default": documents})

# Print results
summarizer.print_summaries(summaries)
```
