# chunking.py
import fitz  # PyMuPDF
import os
import re
from pathlib import Path

# --- Configuration ---
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
print(f"Base Project Directory (SCRIPT_DIR.parent): {SCRIPT_DIR}")

# --- !!! NEW: FAS Name Mapping !!! ---
# You'll need to populate this dictionary with your actual filenames and standard names
# Using Path objects as keys to be robust with path separators
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
# Path to the specific PDF file you want to process
# Ensure this path exists as a key in FAS_NAME_MAPPING if you want the name to be found
PATH_TO_PDF_FILE=SCRIPT_DIR / "data" / "SS" / "SS_12_Musharakah.pdf"
print(f"Target PDF File Path: {PATH_TO_PDF_FILE}")


# --- Helper Functions for Identifying Structure ---

def extract_standard_details_from_doc(doc, pdf_path_obj): # Now takes Path object
    """
    Tries to extract Standard No. and Name.
    Standard No. is primarily from filename.
    Standard Name is from FAS_NAME_MAPPING, then from document content.
    """
    standard_no = "Unknown"
    standard_name = "Unknown"
    filename = pdf_path_obj.name # Get filename like "FAS_32.pdf"

    # 1. Extract Standard Number from filename (more reliable for number)
    fn_match_num = re.search(r"FAS(?:_|\s|-)?(\d+)", filename, re.IGNORECASE)
    if fn_match_num:
        standard_no = fn_match_num.group(1)

    # 2. Get Standard Name from Mapping (most reliable for name if entry exists)
    if pdf_path_obj in FAS_NAME_MAPPING:
        standard_name = FAS_NAME_MAPPING[pdf_path_obj]
    else:
        print(f"  [INFO] Standard name for '{filename}' not found in FAS_NAME_MAPPING. Will try to find in document.")

    # 3. If name not found in mapping, try to find it in the document (first page)
    if standard_name == "Unknown" and doc and len(doc) > 0: # Check if name still unknown
        first_page = doc[0]
        blocks = first_page.get_text("blocks", sort=True)

        pattern_std_line = re.compile(
            r"Financial Accounting Standard No\.\s*\((\w+)\)\s*:?\s*(.*)", re.IGNORECASE
        )
        known_standard_titles_patterns = [ # Examples
            re.compile(r"^\s*Ijarah\s*$", re.IGNORECASE),
            re.compile(r"^\s*Murabaha\s+and\s+Other\s+Deferred\s+Payment\s+Sales\s*$", re.IGNORECASE),
            re.compile(r"^\s*Musharaka\s+Financing\s*$", re.IGNORECASE),
            re.compile(r"^\s*Istisna'a\s+and\s+Parallel\s+Istisna'a\s*$", re.IGNORECASE),
        ]

        for i, block in enumerate(blocks[:15]): 
            text_lines = block[4].strip().split('\n')
            for line_idx, text_line in enumerate(text_lines):
                text_line_cleaned = text_line.strip()
                match_std_line = pattern_std_line.search(text_line_cleaned)

                if match_std_line:
                    doc_std_no = match_std_line.group(1).strip()
                    if standard_no == "Unknown": standard_no = doc_std_no
                    elif standard_no != doc_std_no:
                        print(f"  [WARNING] Filename std no '{standard_no}' differs from doc std no '{doc_std_no}'. Using filename one.")
                    
                    potential_name_from_pattern = match_std_line.group(2).strip()
                    if potential_name_from_pattern and len(potential_name_from_pattern) > 3:
                        standard_name = potential_name_from_pattern
                        # print(f"  [DEBUG] Standard name found in doc (same line): {standard_name}")
                        return standard_no, standard_name 

                if standard_name == "Unknown": # Check only if still unknown
                    for pattern_title in known_standard_titles_patterns:
                        if pattern_title.match(text_line_cleaned):
                            standard_name = text_line_cleaned 
                            # print(f"  [DEBUG] Standard name found in doc (known title match): {standard_name}")
                            return standard_no, standard_name
                    
                    if line_idx + 1 < len(text_lines):
                        next_line_text = text_lines[line_idx + 1].strip()
                        for pattern_title in known_standard_titles_patterns:
                            if pattern_title.match(next_line_text):
                                standard_name = next_line_text
                                # print(f"  [DEBUG] Standard name found in doc (next line known title): {standard_name}")
                                return standard_no, standard_name
        
        if standard_name == "Unknown":
            print(f"  [INFO] Standard name could not be determined from document content for '{filename}'.")

    return standard_no, standard_name


# --- !!! UPDATED MAIN_SECTION_MARKERS AS PER YOUR REQUEST !!! ---
MAIN_SECTION_MARKERS = {
    "Contents": re.compile(r"^\s*Contents\s*$", re.IGNORECASE), 
    "Preface": re.compile(r"^\s*Preface\s*$", re.IGNORECASE),
    "Introduction": re.compile(r"^\s*Introduction\s*$", re.IGNORECASE),
    "Objective of the standard": re.compile(r"^\s*Objective of the standard\s*$", re.IGNORECASE),
    "Scope": re.compile(r"^\s*Scope\s*$", re.IGNORECASE),
    "Definitions": re.compile(r"^\s*Definitions\s*$", re.IGNORECASE),
    "Statement of the Standard": re.compile(r"^\s*Statement of the Standard\s*$", re.IGNORECASE),
    "Effective date": re.compile(r"^\s*Effective date\s*$", re.IGNORECASE), # Added from your previous good list
    "Transitional provisions": re.compile(r"^\s*Transitional provisions\s*$", re.IGNORECASE),
    "Amendments to other standards": re.compile(r"^\s*Amendments to other standards\s*$", re.IGNORECASE),
    
    "Identifying (and separating) an Ijarah": re.compile(rf"^\s*{re.escape("Identifying (and separating) an Ijarah".strip())}\s*$", re.IGNORECASE), # Note: removed trailing space from key
    "Accounting and financial reporting by the lessee": re.compile(rf"^\s*{re.escape("Accounting and financial reporting by the lessee".strip())}\s*$", re.IGNORECASE),
    "Accounting and financial reporting by the lessor": re.compile(rf"^\s*{re.escape("Accounting and financial reporting by the lessor".strip())}\s*$", re.IGNORECASE), # Note: removed trailing space from key
    "Ijarah MBT: transfer of underlying asset’s ownership": re.compile(rf"^\s*{re.escape("Ijarah MBT: transfer of underlying asset’s ownership".strip())}\s*$", re.IGNORECASE),
    "Sale and Ijarah-back transactions": re.compile(rf"^\s*{re.escape("Sale and Ijarah-back transactions".strip())}\s*$", re.IGNORECASE),
    "Murabaha and other deferred payment sales in the financial statements of the seller": re.compile(rf"^\s*{re.escape("Murabaha and other deferred payment sales in the financial statements of the seller".strip())}\s*$", re.IGNORECASE),
    "Murabaha and other deferred payment sales in the financial statements of the buyer": re.compile(rf"^\s*{re.escape("Murabaha and other deferred payment sales in the financial statements of the buyer".strip())}\s*$", re.IGNORECASE),
    "Accounting treatments": re.compile(rf"^\s*{re.escape("Accounting treatments".strip())}\s*$", re.IGNORECASE),

    "Appendices": re.compile(r"^\s*Appendices\s*$", re.IGNORECASE), 
    "Appendix": re.compile(r"^\s*Appendix\s*\(?[A-Z0-9]\)?", re.IGNORECASE), 
}

import re # Ensure re is imported

MAIN_SECTION_MARKERS_SS = {
    "Scope of the Standard": re.compile(rf"^\s*{re.escape("Scope of the Standard".strip())}\s*$", re.IGNORECASE),
    "Procedures Prior to the Contract of Murabahah": re.compile(rf"^\s*{re.escape("Procedures Prior to the Contract of Murabahah".strip())}\s*$", re.IGNORECASE),
    "First Category: Traditional Fiqh-Nominate Partnerships": re.compile(rf"^\s*{re.escape("First Category: Traditional Fiqh-Nominate Partnerships".strip())}\s*$", re.IGNORECASE),
    "Second Category: Modern Corporations": re.compile(rf"^\s*{re.escape("Second Category: Modern Corporations".strip())}\s*$", re.IGNORECASE),
    "Promise to Lease": re.compile(rf"^\s*{re.escape("Promise to Lease".strip())}\s*$", re.IGNORECASE),
    "Acquisition of the Asset": re.compile(rf"^\s*{re.escape("Acquisition of the Asset".strip())}\s*$", re.IGNORECASE),
    "Contract of Salam": re.compile(rf"^\s*{re.escape("Contract of Salam".strip())}\s*$", re.IGNORECASE),
    "Subject Matter of Salam": re.compile(rf"^\s*{re.escape("Subject Matter of Salam".strip())}\s*$", re.IGNORECASE),
    "Changes to al-Muslam Fihi": re.compile(rf"^\s*{re.escape("Changes to al-Muslam Fihi".strip())}\s*$", re.IGNORECASE),
    "Parallel Salam": re.compile(rf"^\s*{re.escape("Parallel Salam".strip())}\s*$", re.IGNORECASE),
    "Salam Sukuk Issues": re.compile(rf"^\s*{re.escape("Salam Sukuk Issues".strip())}\s*$", re.IGNORECASE),
    "Concluding an Ijarah Contract": re.compile(rf"^\s*{re.escape("Concluding an Ijarah Contract".strip())}\s*$", re.IGNORECASE),
    "Definitions, Classifications and Types": re.compile(rf"^\s*{re.escape("Definitions, Classifications and Types".strip())}\s*$", re.IGNORECASE),
    # For "Subject Matter of IjarahSubject Matter of Ijarah", assuming it's a typo and meant to be one.
    # If it can appear as "Subject Matter of IjarahSubject Matter of Ijarah" OR "Subject Matter of Ijarah",
    # you might need two separate entries or a more complex regex.
    # For now, treating it as one phrase:
    "Subject Matter of Ijarah": re.compile(rf"^\s*{re.escape("Subject Matter of Ijarah".strip())}\s*$", re.IGNORECASE),
    "Subject Matter of Ijarah": re.compile(rf"^\s*{re.escape("Subject Matter of Ijarah".strip())}\s*$", re.IGNORECASE),

    "Guarantees and Treatment of Ijarah Receivables": re.compile(rf"^\s*{re.escape("Guarantees and Treatment of Ijarah Receivables".strip())}\s*$", re.IGNORECASE),
    "Diminishing Musharakah": re.compile(rf"^\s*{re.escape("Diminishing Musharakah".strip())}\s*$", re.IGNORECASE),
    "Changes to the Ijarah Contract": re.compile(rf"^\s*{re.escape("Changes to the Ijarah Contract".strip())}\s*$", re.IGNORECASE),
    "Acquisition of Title": re.compile(rf"^\s*{re.escape("Acquisition of Title".strip())}\s*$", re.IGNORECASE),
    "Transfer of the Ownership in the Leased Property": re.compile(rf"^\s*{re.escape("Transfer of the Ownership in the Leased Property".strip())}\s*$", re.IGNORECASE),
    "Conclusion": re.compile(rf"^\s*{re.escape("Conclusion".strip())}\s*$", re.IGNORECASE), # Note: removed trailing space from original set element
    "Guarantees and Treatment": re.compile(rf"^\s*{re.escape("Guarantees and Treatment".strip())}\s*$", re.IGNORECASE),
    

    "Appendices": re.compile(r"^\s*Appendices\s*$", re.IGNORECASE), 
    "Appendix": re.compile(r"^\s*Appendix\s*\(?[A-Z0-9]\)?", re.IGNORECASE), 
}
# --- END OF UPDATED MAIN_SECTION_MARKERS ---


def check_main_section(line):
    """Checks if a line matches a main section marker."""
    cleaned_line = line.strip()
    for name, pattern in MAIN_SECTION_MARKERS_SS.items():
        match = pattern.match(cleaned_line)
        if match:
            # For Appendix or specific titles, capture the full matched line
            # if name in ["Appendix", "Appendices"] or len(cleaned_line.split()) > 3 : 
            # The above condition might be too broad if a key is short like "Scope"
            # Better to return the exact matched line if the key itself is long, or it's an Appendix
            if name in ["Appendix", "Appendices"] or (isinstance(name, str) and len(name.split()) > 3):
                return True, cleaned_line # Return the full matched line from PDF
            return True, name # Return the dictionary key as the section name
    return False, None

HEADING_PATTERNS = [
    ("L3_SlashSlash", re.compile(r"^\s*(\d+\s*/\s*\d+\s*/\s*\d+)\s+(.+)")), 
    ("L2_Slash", re.compile(r"^\s*(\d+\s*/\s*\d+)\s+(.+)")),      
    ("L1_NumDot", re.compile(r"^\s*(\d+)\.\s+(.+)")),         
    ("IN_Num", re.compile(r"^\s*(IN\d+)\s+(.+)"))           
]

def check_heading(line):
    cleaned_line = line.strip()
    # Heuristic to avoid matching list items in appendices that might have leading numbers by mistake
    # This is a bit of a hack; proper list item detection would be better.
    # If line starts with "Mr. " or "Ms. " or "Dr. " and contains "–" (em-dash or en-dash for chairman etc.)
    if (cleaned_line.startswith(("Mr. ", "Ms. ", "Dr. ")) and ("–" in cleaned_line or "-" in cleaned_line)) or \
       (re.match(r"^\s*[a-z]\)\s+", cleaned_line)) or \
       (re.match(r"^\s*([ivx]+)\)\s+", cleaned_line, re.IGNORECASE)): # e.g. a) or i)
        # Check if it still strongly looks like a L1_NumDot
        l1_match = HEADING_PATTERNS[2][1].match(cleaned_line) # HEADING_PATTERNS[2] is L1_NumDot
        if l1_match and len(l1_match.group(2).split()) < 5: # If title part is very short
            return False, None, None, None, None # Likely a list item, not a true heading

    for level_name, pattern in HEADING_PATTERNS:
        match = pattern.match(cleaned_line)
        if match:
            full_heading_text = cleaned_line
            heading_prefix = match.group(1).strip()
            title_part = match.group(2).strip()

            if "................" in title_part: 
                continue
            if len(title_part.split()) > 20: # Heuristic: title part not too long
                if level_name == "L1_NumDot" and len(cleaned_line.split()) > 25:
                    continue
                elif len(title_part.split()) > 25:
                    continue
            
            # Additional check for L1_NumDot to avoid simple numbered list items
            if level_name == "L1_NumDot":
                # If title_part is very short (e.g., < 4 words) and doesn't end with typical sentence punctuation
                # it might be a list item. This is a heuristic.
                if len(title_part.split()) < 4 and not title_part.endswith(('.', '?', '!', ':')):
                    # Check if previous line was also a potential list item or short
                    # This requires access to previous block, complex here. For now, this simple check.
                    pass # Allow it for now, but this is an area for refinement for lists vs headings

            return True, level_name, full_heading_text, heading_prefix, title_part
    return False, None, None, None, None



# Ensure this helper is defined outside or at the top of the file
def is_appendix_section(section_name):
    if not section_name:
        return False
    return section_name.lower().startswith("appendix")

# --- Main Processing Function (REVISED to fix TypeError and refine L1 promotion) ---
def process_pdf_to_chunks(pdf_path_obj): # Takes Path object
    print(f"\n--- Processing Document: {pdf_path_obj.name} ---")
    try:
        doc = fitz.open(pdf_path_obj)
    except Exception as e:
        print(f"Error opening PDF {pdf_path_obj}: {e}")
        return []

    chunks = []
    source_file = pdf_path_obj.name
    extracted_std_no, extracted_std_name = extract_standard_details_from_doc(doc, pdf_path_obj)

    print(f"  Standard No: {extracted_std_no}, Standard Name: {extracted_std_name}")

    current_chunk_lines = []
    current_chunk_start_page = 0
    
    active_main_section = "General" 
    active_heading_path = []
    skipping_toc = False 
    new_main_section_started_but_no_content_yet = False

    for page_num, page in enumerate(doc):
        page_no_for_display = page_num + 1
        blocks = page.get_text("blocks", sort=True)

        for b_idx, block in enumerate(blocks):
            if block[6] != 0: 
                continue

            block_text_original = block[4] 
            block_text_cleaned_for_check = block_text_original.strip()

            if not block_text_cleaned_for_check:
                continue

            if skipping_toc: 
                is_next_main_sec_after_toc, next_main_sec_name_after_toc = check_main_section(block_text_cleaned_for_check)
                if is_next_main_sec_after_toc and next_main_sec_name_after_toc != "Contents":
                    skipping_toc = False 
                    active_main_section = next_main_sec_name_after_toc
                    active_heading_path = []
                    current_chunk_start_page = page_no_for_display
                    current_chunk_lines.append(block_text_original) 
                    new_main_section_started_but_no_content_yet = True
                    continue 
                else:
                    continue 

            is_explicit_main_sec, explicit_main_sec_name = check_main_section(block_text_cleaned_for_check)
            is_numbered_heading, num_head_level, num_head_full_text, num_head_prefix, num_head_title = False, None, None, None, None
            
            if not is_explicit_main_sec:
                 is_numbered_heading, num_head_level, num_head_full_text, num_head_prefix, num_head_title = check_heading(block_text_cleaned_for_check)
            
            is_new_main_section_context = False 
            effective_main_section_name_for_this_block = active_main_section 

            if is_explicit_main_sec:
                is_new_main_section_context = True
                effective_main_section_name_for_this_block = explicit_main_sec_name
            
            elif is_numbered_heading and num_head_level == "L1_NumDot":
                should_promote_l1 = False
                generic_or_pre_standard_sections = ["General", "Preface", "Introduction", "Statement of the Standard"]
                
                if active_main_section in generic_or_pre_standard_sections:
                    should_promote_l1 = True
                elif is_appendix_section(active_main_section):
                    should_promote_l1 = True 
                elif num_head_title != active_main_section and \
                     active_main_section not in generic_or_pre_standard_sections and \
                     not is_appendix_section(active_main_section) and \
                     not is_appendix_section(num_head_title): # Check the new title too
                    should_promote_l1 = True

                if should_promote_l1 and num_head_title and len(num_head_title.split()) > 0: 
                    is_new_main_section_context = True
                    effective_main_section_name_for_this_block = num_head_title
            
            should_finalize_previous_chunk = False
            if is_new_main_section_context:
                if current_chunk_lines: 
                    should_finalize_previous_chunk = True
            elif is_numbered_heading: 
                if not new_main_section_started_but_no_content_yet and current_chunk_lines:
                    should_finalize_previous_chunk = True
            
            if should_finalize_previous_chunk:
                content = "".join(current_chunk_lines).strip()
                if content: 
                    metadata = {
                        "source_file": source_file,
                        "standard_no": extracted_std_no,
                        "standard_name": extracted_std_name,
                        "page_start": current_chunk_start_page,
                        "page_end": page_no_for_display, 
                        "main_section": active_main_section, 
                        "heading_path": list(active_heading_path) 
                    }
                    chunks.append({"metadata": metadata, "content": content})
                current_chunk_lines = []

            if is_new_main_section_context:
                if effective_main_section_name_for_this_block == "Contents":
                    skipping_toc = True
                    active_main_section = "Contents" 
                    active_heading_path = [] 
                    current_chunk_lines = [] 
                    new_main_section_started_but_no_content_yet = False 
                    continue 
                
                active_main_section = effective_main_section_name_for_this_block
                active_heading_path = [] 
                if not current_chunk_lines: current_chunk_start_page = page_no_for_display
                current_chunk_lines.append(block_text_original) 
                new_main_section_started_but_no_content_yet = True

                # If this new main section context was established by promoting an L1_NumDot
                # and it wasn't an explicit main section marker
                if is_numbered_heading and num_head_level == "L1_NumDot" and \
                   not is_explicit_main_sec and \
                   effective_main_section_name_for_this_block == num_head_title:
                    active_heading_path.append((num_head_level, num_head_title))
            
            elif is_numbered_heading: 
                active_heading_path_backup = list(active_heading_path)
                if num_head_level in ["L1_NumDot", "IN_Num"]: 
                    active_heading_path = [(num_head_level, num_head_title)]
                elif num_head_level == "L2_Slash":
                    new_path = [h for h in active_heading_path_backup if h[0] in ["L1_NumDot", "IN_Num"]]
                    new_path.append((num_head_level, num_head_title))
                    active_heading_path = new_path
                elif num_head_level == "L3_SlashSlash":
                    new_path = [h for h in active_heading_path_backup if h[0] in ["L1_NumDot", "IN_Num", "L2_Slash"]]
                    new_path.append((num_head_level, num_head_title))
                    active_heading_path = new_path
                
                if not current_chunk_lines: current_chunk_start_page = page_no_for_display
                current_chunk_lines.append(block_text_original) 
                new_main_section_started_but_no_content_yet = False 
            
            else: 
                if not skipping_toc: 
                    if not current_chunk_lines: 
                        current_chunk_start_page = page_no_for_display
                    current_chunk_lines.append(block_text_original)
                    new_main_section_started_but_no_content_yet = False 

    if current_chunk_lines and not skipping_toc: 
        content = "".join(current_chunk_lines).strip()
        if content:
            metadata = {
                "source_file": source_file,
                "standard_no": extracted_std_no,
                "standard_name": extracted_std_name,
                "page_start": current_chunk_start_page,
                "page_end": page_no_for_display, 
                "main_section": active_main_section,
                "heading_path": list(active_heading_path)
            }
            chunks.append({"metadata": metadata, "content": content})
            
    doc.close()
    print(f"  Finished. Found {len(chunks)} chunks.")
    return chunks


# --- Main Execution ---
if __name__=="__main__":
    if not PATH_TO_PDF_FILE.is_file(): 
        print(f"ERROR: PDF file not found or is not a file: {PATH_TO_PDF_FILE}")
        print(f"Please ensure the path is correct and the file exists.")
        print(f"Also check if an entry exists in FAS_NAME_MAPPING for this file path if you expect a specific name.")
    else:
        all_processed_chunks = []
        
        print(f"Processing single file: {PATH_TO_PDF_FILE.name}")
        chunks_from_file = process_pdf_to_chunks(PATH_TO_PDF_FILE) 
        all_processed_chunks.extend(chunks_from_file)

        if chunks_from_file:
            print(f"\n  Chunks Preview from: {PATH_TO_PDF_FILE.name}")
            for i, chunk_data in enumerate(chunks_from_file[:5]): 
                print(f"\n  --- Chunk {i+1} ({PATH_TO_PDF_FILE.name}) ---")
                print(f"  Metadata: {chunk_data['metadata']}")
                print(f"  Content (first 200 chars):\n    {repr(chunk_data['content'][:200])}...")
                print("  " + "-" * 30)
        
        print(f"\n\n==========================================================")
        if not chunks_from_file:
            print(f"No chunks were extracted from {PATH_TO_PDF_FILE.name}.")
        else:
            print(f"Total chunks extracted from {PATH_TO_PDF_FILE.name}: {len(all_processed_chunks)}")
        print(f"==========================================================")

        if all_processed_chunks: # For Detailed View
            print("\n\n--- Detailed View of the First Actual Content Chunk (if any) ---")
            first_content_chunk = None
            for chunk in all_processed_chunks:
                if chunk['metadata']['main_section'] not in ["General", "Contents"]:
                    first_content_chunk = chunk
                    break
            if not first_content_chunk and all_processed_chunks: 
                first_content_chunk = all_processed_chunks[0]

            if first_content_chunk:
                print(f"Metadata: {first_content_chunk['metadata']}")
                print(f"Full Content:\n{first_content_chunk['content']}")
                print("--- End of First Actual Content Chunk Detailed View ---")
            else:
                print("No suitable first content chunk found for detailed view.")

# --- !!! SNIPPET TO LIST MAIN_SECTION OF ALL CHUNKS (with Chunk Length) !!! ---
        print(f"\n\n==========================================================")
        print(f"Overview of Main Sections for All Chunks from: {PATH_TO_PDF_FILE.name}")
        print(f"==========================================================")

        if not all_processed_chunks:
            print("No chunks were processed to display main sections.")
        else:
            # Added "Length" column and adjusted spacing
            print(f"{'Chunk #':<8} | {'Page':<7} | {'Length':<8} | {'Main Section':<55} | {'Heading Path (First Element if any)':<65}")
            print(f"{'-'*7:<8} | {'-'*6:<7} | {'-'*7:<8} | {'-'*54:<55} | {'-'*64:<65}")
            for i, chunk_data in enumerate(all_processed_chunks):
                chunk_num = i + 1
                main_section = chunk_data['metadata'].get('main_section', 'N/A')
                page_s = chunk_data['metadata'].get('page_start', '')
                page_e = chunk_data['metadata'].get('page_end', '')
                page_display = f"{page_s}-{page_e}" if page_s != page_e else str(page_s)

                # Get chunk content and its length
                content = chunk_data.get('content', '')
                chunk_length = len(content)

                heading_path = chunk_data['metadata'].get('heading_path', [])
                first_heading_in_path = ""
                if heading_path:
                    first_heading_in_path = str(heading_path[0]) 
                
                # Adjust truncation based on new column widths
                main_section_display = (main_section[:52] + '...') if len(main_section) > 55 else main_section
                first_heading_display = (first_heading_in_path[:62] + '...') if len(first_heading_in_path) > 65 else first_heading_in_path
                
                print(f"{chunk_num:<8} | {page_display:<7} | {chunk_length:<8} | {main_section_display:<55} | {first_heading_display:<65}")
        # --- !!! END OF SNIPPET !!! ---


        # --- SNIPPET TO PRINT SPECIFIC CHUNKS FOR REVIEW ---
        print(f"\n\n==========================================================")
        print(f"Reviewing Specific Chunks from: {PATH_TO_PDF_FILE.name}")
        print(f"==========================================================")

        chunks_to_review_indices = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] # Adjusted for more review
                                            
        if not all_processed_chunks:
            print("No chunks were processed, cannot review specific chunks.")
        else:
            for chunk_idx in chunks_to_review_indices:
                if chunk_idx < len(all_processed_chunks):
                    chunk_data = all_processed_chunks[chunk_idx]
                    print(f"\n--- Reviewing Chunk {chunk_idx + 1} (Index {chunk_idx}) ---")
                    print(f"  Metadata: {chunk_data['metadata']}")
                    content_preview = repr(chunk_data['content'][:300]) 
                    print(f"  Content (first 300 chars):\n    {content_preview}...")
                    print("  " + "-" * 40)
                else:
                    print(f"\n--- Chunk {chunk_idx + 1} (Index {chunk_idx}) not available (Total chunks: {len(all_processed_chunks)}) ---")
        # --- END OF SNIPPET TO PRINT SPECIFIC CHUNKS ---