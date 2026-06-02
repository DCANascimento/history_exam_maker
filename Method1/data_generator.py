from text_extractor import TextExtractor
from meaning_extractor import MeaningExtractor

def main():
    t_extractor = TextExtractor()
    m_extractor = MeaningExtractor()

    corpora = t_extractor.get_text("example2.txt")
    #print(f"--- Processing Text ---\n{corpora}\n")
    
    # 1. Handle Entities
    m_extractor.prepare_entities(corpora)
    entities = m_extractor.get_entities()

    print(f"--- Entities Found: {len(entities)} ---")

    # 2. Handle Relations
    print("Extracting relations via Linguakit...")
    m_extractor.prepare_relations(corpora)
    relations = m_extractor.get_relations()

    print(f"--- Relations (Triples) Found: {len(relations)} ---")

    # 3. Export to intermediate file
    m_extractor.save_knowledge_base("knowledge_base.txt")

if __name__ == "__main__":
    main()