import re
import spacy

def extract_context_sentences(input_file="../text_samples/example2.txt", output_file="year_sentences.txt", require_both=False):

    print("Loading Portuguese NLP Model...")
    nlp = spacy.load("pt_core_news_lg")
    
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Clean up line breaks and double spaces
    clean_text = re.sub(r'\s+', ' ', raw_text).strip()

    # Prevent premature sentence breaks at common abbreviations
    sentence_end_pattern = r'(?<!\b[D|S|V|R]\.)(?<!\bFr\.)(?<!\bFrei\.)(?<=[.!?])\s+(?=[A-Z“"–—])'
    all_sentences = re.split(sentence_end_pattern, clean_text)

    valid_sentences = []

    print(f"Analyzing {len(all_sentences)} sentences for dates and locations...")
    
    # Process sentences using spacy's pipeline batching for speed
    for doc in nlp.pipe(all_sentences, batch_size=50):
        sentence_text = doc.text.strip()
        if not sentence_text:
            continue
            
        # 1. Look for a 4-digit year pattern using regex
        has_year = bool(re.search(r'\b\d{4}\b', sentence_text))
        
        # 2. Look for explicit locations recognized by the NER engine
        has_location = any(ent.label_ == "LOC" for ent in doc.ents)
        
        # 3. Apply validation logic based on target criteria
        should_extract = (has_year and has_location) if require_both else (has_year or has_location)
        
        if should_extract:
            # Clean up leading formatting junk symbols if present
            cleaned_sentence = re.sub(r'^[—\-\s•👉]+', '', sentence_text).strip()
            if cleaned_sentence:
                valid_sentences.append(cleaned_sentence)

    # Deduplicate while preserving text sequence order
    valid_sentences = list(dict.fromkeys(valid_sentences))

    # Save the structured sentences
    with open(output_file, "w", encoding="utf-8") as f:
        for sentence in valid_sentences:
            f.write(f"{sentence}\n\n")

    print(f"Saved {len(valid_sentences)} contextual sentences into '{output_file}'.")

if __name__ == "__main__":
    # require_both=True forces sentences to have a year and a location
    extract_context_sentences(require_both=False)