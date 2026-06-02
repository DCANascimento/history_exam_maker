import random
import re
import spacy

def load_sentences(file_path="year_sentences.txt"):
    """Reads the custom sentence file and returns a list of clean strings."""
    sentences = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Sentence"):
                    line = re.sub(r'^Sentence\s+\d+:\s*', '', line)
                sentences.append(line)
    except FileNotFoundError:
        # Fallback array for immediate testing
        sentences = [
            "Foi então que o inquieto conego hespanhol buscou associar á empreza varios sacerdotes, que, por fim estabeleceram uma especie de congregação em Tolosa, com a qual, sendo os seus estatutos aprovados em 1216 por Honorio iii se constituiu a ordem dos frades prégadores ou dominicanos.",
            "Nesta juncta se approvaram os regulamentos já preparados, e, com o titulo de Instrucções, promulgou-se o primeiro codigo inquisitorial d’Hespanha (outubro de 1484).",
            "Sobre isso são expressos e terminantes alguns canones do iv concilio geral de Latrão e outros monumentos ecclesiasticos daquella epocha.",
            "Entretanto, nas cortes de Toledo, reunidas nos principios de 1480, procurava-se obstar a que o tracto e convivencia constante dos novos convertidos com os seus antigos co-religionarios fosse incentivo para recahirem no judaismo."
        ]
    return sentences

def extract_year(text):
    match = re.search(r'\b\d{3,4}\b', text)
    return match.group(0) if match else None

def smooth_portuguese_grammar(text):
    """Resolves standard Portuguese contraction gaps automatically (de a -> da, etc.)."""
    text = re.sub(r'\bde\s+o\b', 'do', text, flags=re.IGNORECASE)
    text = re.sub(r'\bde\s+a\b', 'da', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+o\b', 'no', text, flags=re.IGNORECASE)
    text = re.sub(r'\bem\s+a\b', 'na', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor\s+o\b', 'pelo', text, flags=re.IGNORECASE)
    text = re.sub(r'\bpor\s+a\b', 'pela', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+o\b', 'ao', text, flags=re.IGNORECASE)
    text = re.sub(r'\ba\s+a\b', 'à', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', text).strip()

def generate_unified_exam(file_path="year_sentences.txt", mode="mixed", num_questions=5, max_char_len=260):
    """
    Generates historical questions dynamically targeting both locations and years.
    Sentences longer than max_char_len are dropped entirely—never truncated.
    """
    nlp = spacy.load("pt_core_news_lg")
    raw_sentences = load_sentences(file_path)
    
    # 1. Gather global item pools across the entire dataset to feed wrong choices
    global_locations = set()
    global_years = set()
    
    docs = list(nlp.pipe(raw_sentences, batch_size=50))
    for doc in docs:
        yr = extract_year(doc.text)
        if yr:
            global_years.add(yr)
        for ent in doc.ents:
            if ent.label_ == "LOC" and len(ent.text.strip()) > 2:
                global_locations.add(ent.text.strip())

    pool_questions = []

    # 2. Extract potential questions from every valid context window
    for doc in docs:
        sentence = doc.text.strip()
        
        # FILTER OUT LENGTHY PHRASES: Drop giant text chunks completely
        if len(sentence) > max_char_len:
            continue
            
        locs_in_sentence = [ent.text.strip() for ent in doc.ents if ent.label_ == "LOC"]
        sentence_year = extract_year(sentence)
        
        # Detect what questions this specific sentence is capable of hosting
        can_do_location = len(locs_in_sentence) > 0
        can_do_year = sentence_year is not None
        
        if not (can_do_location or can_do_year):
            continue

        # Choose the question target based on configuration mode or coin flip
        assigned_type = None
        if mode == "location" and can_do_location:
            assigned_type = "location"
        elif mode == "year" and can_do_year:
            assigned_type = "year"
        elif mode == "mixed":
            options = []
            if can_do_location: options.append("location")
            if can_do_year: options.append("year")
            assigned_type = random.choice(options)
            
        if not assigned_type:
            continue

        # 3. Construct specific question schema without cutting any text
        context_text = sentence
        answer = None
        instruction = ""
        
        if assigned_type == "location":
            answer = locs_in_sentence[0]
            context_text = re.sub(r'\b' + re.escape(answer) + r'\b', '_______', sentence)
            instruction = "determine a localização geográfica ou localidade omitida"
        else:
            answer = sentence_year
            context_text = re.sub(r'\(\s*' + re.escape(answer) + r'\s*\)', '', sentence)
            context_text = re.sub(r'\b' + re.escape(answer) + r'\b', '____', context_text)
            instruction = "determine o ano ou marco cronológico omitido"

        # Apply Portuguese grammar contraction smoothing to the final text block
        context_text = smooth_portuguese_grammar(context_text)

        pool_questions.append({
            "type": assigned_type,
            "context": context_text,
            "answer": answer,
            "instruction": instruction
        })

    if not pool_questions:
        print("No questions passed the criteria under mode.")
        return

    # 4. Compile and shuffle final selection
    random.shuffle(pool_questions)
    actual_num = min(num_questions, len(pool_questions))
    
    print("\n=======================================================")
    print("EXAME DE HISTÓRIA 2")
    print("=======================================================\n")

    for i, q in enumerate(pool_questions[:actual_num], 1):
        correct = q['answer']
        
        # Build contextual wrong distractors
        if q['type'] == "location":
            wrong_pool = [loc for loc in global_locations if loc != correct]
            backup = ["Coimbra", "Évora", "Lisboa", "Madrid", "Roma"]
            while len(wrong_pool) < 3:
                item = random.choice(backup)
                if item != correct and item not in wrong_pool:
                    wrong_pool.append(item)
            prefix = "Localidade:"
        else:
            wrong_pool = [yr for yr in global_years if yr != correct]
            while len(wrong_pool) < 3:
                wrong_pool.append(str(random.randint(1100, 1500)))
            prefix = "Ano de:"

        options = [correct] + random.sample(wrong_pool, 3)
        random.shuffle(options)
        
        print(f"Questão {i}: De acordo com o que aprendeu, {q['instruction']}:")
        print(f"\"{q['context']}\"\n")
        
        letters = ['A', 'B', 'C', 'D']
        correct_letter = "A"
        
        for letter, option in zip(letters, options):
            print(f"  {letter}) {prefix} {option}")
            if option == correct:
                correct_letter = letter
                
        print(f"\nResposta correta: ({correct_letter})")
        print(f"-------------------------------------------------------\n")

if __name__ == "__main__":
    generate_unified_exam(mode="mixed", num_questions=10, max_char_len=260)