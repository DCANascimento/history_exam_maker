import random
import re

def load_knowledge_base(file_path="knowledge_base_quads.txt"):
    events = []
    current_section = None
    
    with open(file_path, "r", encoding="utf-8") as f:
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
                parts = [p.strip() for p in line.split('|')]
                if len(parts) == 4:
                    events.append({
                        "subject": parts[0],
                        "relation": parts[1],
                        "object": parts[2],
                        "year": parts[3]
                    })
    return events

def smooth_portuguese_grammar(text):
    """
    Applies standard Portuguese contraction rules to merge loose prepositions
    and fixes irregular double spaces left after replacements.
    """
    # 1. 'de' contractions
    text = re.sub(r'\bde\s+o\b', 'do', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+a\b', 'da', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+os\b', 'dos', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+as\b', 'das', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+este\b', 'deste', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+esse\b', 'desse', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+aquele\b', 'daquele', text, flags=re.IGNORECASE)
    
    # 2. 'em' contractions
    text = re.sub(r'\bem\s+o\b', 'no', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+a\b', 'na', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+os\b', 'nos', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+as\b', 'nas', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+este\b', 'neste', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+esse\b', 'nesse', text, flags=re.IGNORECASE)
    
    # 3. 'por' contractions
    text = re.sub(r'\bpor\s+o\b', 'pelo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor\s+a\b', 'pela', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor\s+os\b', 'pelos', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor\s+as\b', 'pelas', text, flags=re.IGNORECASE)
    
    # 4. 'a' contractions (crases)
    text = re.sub(r'\ba\s+o\b', 'ao', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+os\b', 'aos', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+a\b', 'à', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+as\b', 'às', text, flags=re.IGNORECASE)

    # Collapse any double spacing created during text assembly
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_simple_exam(file_path="knowledge_base_quads.txt", num_questions=5):
    events = load_knowledge_base(file_path)
    
    if not events:
        print("No valid historical events found in the filtered file.")
        return

    all_years = list(set(e['year'] for e in events))
    random.shuffle(events)
    
    print("\n=======================================================")
    print("EXAME DE HISTÓRIA 1")
    print("=======================================================\n")
    
    actual_num_questions = min(num_questions, len(events))
    
    for i, e in enumerate(events[:actual_num_questions], 1):
        correct = e['year']
        
        wrong_pool = [year for year in all_years if year != correct]
        if len(wrong_pool) < 3:
            wrong_pool = ["1200", "1345", "1492"]
            
        options = [correct] + random.sample(wrong_pool, 3)
        random.shuffle(options)

        # Handle subject placement and case validation
        subj = e['subject'].strip()
        if subj.lower() == "o acontecimento" or not subj:
            subj_text = ""
        else:
            first_word = subj.split()[0]

            if first_word.lower() in ["o", "a", "os", "as", "um", "uma", "este", "esse"]:
                subj_text = " " + subj[0].lower() + subj[1:]
            else:
                subj_text = " " + subj
        
        # Build raw sentence structure strings
        raw_question = f"Em que ano é que{subj_text} {e['relation']} {e['object']}?"
        
        # Pass the unified question string through the Grammar Smoothing Engine
        polished_question = smooth_portuguese_grammar(raw_question)
        
        print(f"Questão {i}: {polished_question}\n")
        
        letters = ['A', 'B', 'C', 'D']
        correct_letter = "A"
        
        for letter, option in zip(letters, options):
            print(f"  {letter}) Ano de {option}")
            if option == correct:
                correct_letter = letter
                
        print(f"Resposta correta: ({correct_letter})")
        print("-------------------------------------------------------\n")

if __name__ == "__main__":
    generate_simple_exam("knowledge_base_quads.txt", 10)