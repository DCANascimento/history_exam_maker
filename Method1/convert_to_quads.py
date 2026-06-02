import re

def clean_text(text):
    """Cleans up formatting artifacts, dashes, and extra spaces."""
    if not text:
        return ""
    text = re.sub(r'^[—\-\s•👉]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_year(text):
    """Extracts a 3 or 4 digit year from a text string."""
    match = re.search(r'\b\d{3,4}\b', text)
    return match.group(0) if match else None

def scrub_year_leaks(text, year):
    """
    Finds and aggressively removes explicit dates and year numbers from the 
    text component so they do not leak the answer inside the exam questions.
    """
    if not text:
        return ""
    
    # 1. Erase parenthetical years completely, e.g., "(1376)" -> ""
    text = re.sub(r'\(\s*' + re.escape(year) + r'\s*\)', '', text)
    
    # 2. Erase full structured dates containing the target year,
    # e.g., "A 31 de março de 1492" or "2 de agosto de 1483"
    date_pattern = r'\b(A\s+)?\d{1,2}\s+de\s+[a-zA-Zçõáéíóú]+\s+de\s+' + re.escape(year)
    text = re.sub(date_pattern, '', text, flags=re.IGNORECASE)
    
    # 3. Catch-all: Erase any remaining standalone occurrences of that specific 4-digit number
    text = re.sub(r'\b' + re.escape(year) + r'\b', '', text)
    
    # 4. Clean up trailing prepositions left dangling after removing the date text
    text = re.sub(r'\b(em|de|da|do|a|o|por|para|com|entre)\s*$', '', text, flags=re.IGNORECASE)
    
    return clean_text(text)

def is_high_quality(sub, rel, obj, year):
    """Enforces strict structural rules to block low-quality, leaked or fragmented data."""
    # 1. All fields must contain substantive content
    if not (sub and rel and obj and year):
        return False
        
    # 2. Prevent abstract fragments or single characters/roman numerals from passing
    if len(sub) < 4 or len(rel) < 2 or len(obj) < 4:
        return False
        
    # 3. Filter out known structural garbage words left over from poor automated extractions
    garbage_words = ['contratou', 'titulou', 'iii', 'iv', 'v', 'anonymous']
    if any(w in sub.lower() or w in rel.lower() for w in garbage_words):
        return False

    # 4. Ensure the relation actually contains an action concept, not just a weak connector
    if rel.lower() in ['de', 'em', 'a', 'o', 'por', 'com']:
        return False

    return True

def process_triples_to_quads(input_file="knowledge_base.txt", output_file="knowledge_base_quads.txt"):
    triples = []
    current_section = None
    
    # Phase 1: Read and parse the input file section
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("---") or line.startswith("SUBJECT"):
                continue
            if "=== TRIPLES ===" in line:
                current_section = "triples"
                continue
            if "===" in line and "TRIPLES" not in line:
                current_section = None
                continue
                
            if current_section == "triples":
                parts = [clean_text(p) for p in line.split('|')]
                if len(parts) == 3:
                    triples.append({"s": parts[0], "r": parts[1], "o": parts[2]})

    high_quality_quads = []

    # Phase 2: Process, sanitize, and upgrade triples into quadruples
    for t in triples:
        # Scan all three fields to find if a numeric year exists anywhere
        found_year = extract_year(t['s']) or extract_year(t['o']) or extract_year(t['r'])
        
        if not found_year:
            continue # Skip triples that do not anchor an event in time
            
        # Run the erasure engine over all semantic fields to strip out the target year leaks
        sub_scrubbed = scrub_year_leaks(t['s'], found_year)
        rel_scrubbed = scrub_year_leaks(t['r'], found_year)
        obj_scrubbed = scrub_year_leaks(t['o'], found_year)
        
        # Sentence Re-stitching & Fallback Assignment
        subject = sub_scrubbed if sub_scrubbed else ""
        relation = rel_scrubbed.lower()
        obj = obj_scrubbed if obj_scrubbed else ""
        year = found_year

        subject = clean_text(subject).capitalize()

        # Phase 3: Run the output through the Quality Assurance Filter
        if is_high_quality(subject, relation, obj, year):
            high_quality_quads.append(f"{subject} | {relation} | {obj} | {year}")

    # Deduplicate matching events while keeping original file order
    high_quality_quads = list(dict.fromkeys(high_quality_quads))

    # Phase 4: Write the premium quadruples database
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== QUADS ===\n")
        for quad in high_quality_quads:
            f.write(f"{quad}\n")
            
    print(f"Filtered out leaks & garbage. Retained {len(high_quality_quads)} quality historical quads in '{output_file}'.")

if __name__ == "__main__":
    process_triples_to_quads()