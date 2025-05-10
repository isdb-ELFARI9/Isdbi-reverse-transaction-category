# chunking.py
import fitz  # PyMuPDF
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

# --- Configuration ---
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
CHUNK_SIZE = 1000  # Number of characters per chunk
CHUNK_OVERLAP = 200  # Number of characters to overlap between chunks

# --- Standard Name Mapping ---
FAS_NAME_MAPPING = {
    SCRIPT_DIR / "data" / "FAS" / "FAS_32.pdf": "FAS_32_Ijarah",
    SCRIPT_DIR / "data" / "FAS" / "FAS_28_Murabaha_Deferred_Payment_Sales.pdf": "FAS_28_Murabaha_Deferred_Payment_Sales",
    SCRIPT_DIR / "data" / "FAS" / "FAS_10_Istisna.pdf": "FAS_10_Istisna",
    SCRIPT_DIR / "data" / "FAS" / "FAS_7_Salam_Parallel_Salam.pdf": "FAS_7_Salam_Parallel_Salam",
    SCRIPT_DIR / "data" / "FAS" / "FAS_4_Musharaka.pdf": "FAS_4_Musharaka",
}

SS_NAME_MAPPING = {
    SCRIPT_DIR / "data" / "SS" / "SS_8_Murabahah.pdf": "SS_8_Murabahah",
    SCRIPT_DIR / "data" / "SS" / "SS_9_Ijarah_Ijarah_Muntahia_Bittamleek.pdf": "SS_9_Ijarah_Ijarah_Muntahia_Bittamleek",
    SCRIPT_DIR / "data" / "SS" / "SS_10_Salam_Parallel_Salam.pdf": "SS_10_Salam_Parallel_Salam",
    SCRIPT_DIR / "data" / "SS" / "SS_12_Musharakah.pdf": "SS_12_Musharakah",
}

def extract_standard_details(pdf_path_obj: Path) -> Tuple[str, str]:
    """Extract standard number and name from filename."""
    standard_no = "Unknown"
    standard_name = "Unknown"
    filename = pdf_path_obj.name

    # Extract Standard Number from filename
    fn_match_num = re.search(r"(?:FAS|SS)(?:_|\s|-)?(\d+)", filename, re.IGNORECASE)
    if fn_match_num:
        standard_no = fn_match_num.group(1)

    # Get Standard Name from Mapping
    if pdf_path_obj in FAS_NAME_MAPPING:
        standard_name = FAS_NAME_MAPPING[pdf_path_obj]
    elif pdf_path_obj in SS_NAME_MAPPING:
        standard_name = SS_NAME_MAPPING[pdf_path_obj]

    return standard_no, standard_name

def create_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Create overlapping chunks from text."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks

def process_pdf_to_chunks(pdf_path_obj: Path) -> List[Dict]:
    """Process PDF into chunks with metadata."""
    print(f"\n--- Processing Document: {pdf_path_obj.name} ---")
    
    try:
        doc = fitz.open(pdf_path_obj)
    except Exception as e:
        print(f"Error opening PDF {pdf_path_obj}: {e}")
        return []

    # Extract standard details
    standard_no, standard_name = extract_standard_details(pdf_path_obj)
    print(f"  Standard No: {standard_no}, Standard Name: {standard_name}")

    # Determine document type (FAS or SS)
    is_fas = "FAS" in standard_name
    document_type = "FAS" if is_fas else "SS"

    # Get all text from the document
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    doc.close()

    # Create chunks from the full text
    text_chunks = create_chunks(full_text)
    
    # Create chunk objects with metadata
    chunks = []
    for i, chunk in enumerate(text_chunks):
                    metadata = {
            "source_file": pdf_path_obj.name,
            "standard_no": standard_no,
            "standard_name": standard_name,
            "document_type": document_type,
            "page_start": "1",  # Since we're not tracking pages in simple chunking
            "page_end": "1",    # Since we're not tracking pages in simple chunking
            "main_section": "Full Document",  # Since we're not tracking sections in simple chunking
            "chunk_index": i,
            "total_chunks": len(text_chunks),
            "text_snippet": chunk[:500]  # Store first 500 chars as snippet
        }
        
        chunks.append({
            "metadata": metadata,
            "content": chunk
        })

    print(f"  Finished. Found {len(chunks)} chunks.")
    return chunks

def process_all_documents() -> Tuple[List[Dict], List[Dict]]:
    """Process all FAS and SS documents and return their chunks."""
    # Process FAS documents
    fas_chunks = []
    for pdf_path in FAS_NAME_MAPPING.keys():
        if pdf_path.is_file():
            chunks = process_pdf_to_chunks(pdf_path)
            fas_chunks.extend(chunks)
    
    # Process SS documents
    ss_chunks = []
    for pdf_path in SS_NAME_MAPPING.keys():
        if pdf_path.is_file():
            chunks = process_pdf_to_chunks(pdf_path)
            ss_chunks.extend(chunks)
    
    return fas_chunks, ss_chunks

if __name__ == "__main__":
    fas_chunks, ss_chunks = process_all_documents()
    
    # Print summary
    print("\n=== Processing Summary ===")
    print(f"Total FAS chunks: {len(fas_chunks)}")
    print(f"Total SS chunks: {len(ss_chunks)}")
    print(f"Total chunks: {len(fas_chunks) + len(ss_chunks)}")