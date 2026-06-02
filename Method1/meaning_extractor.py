import os
import subprocess
import spacy
import re
from spacy.matcher import Matcher

class MeaningExtractor:
    def __init__(self):
        self.entities = []
        self.relations = []
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.linguakit_path = os.path.abspath(os.path.join(script_dir, "..", "Linguakit"))
        
        self.model = spacy.load("pt_core_news_lg")
        
        self.matcher = Matcher(self.model.vocab)
        self.matcher.add("DATE_YEAR", [[{"SHAPE": "dddd"}]])

    def prepare_entities(self, text):
        doc = self.model(text)
        for ent in doc.ents:
            entity = ent.text.strip()
            label = ent.label_
            if "reino" in entity.lower() or "império" in entity.lower():
                label = "ORG"
            if (entity, label) not in self.entities:
                self.entities.append((entity, label))
        
        matches = self.matcher(doc)
        for match1, start, end in matches:
            entity = doc[start:end].text.strip()
            if not any(entity.lower() == e[0].lower() for e in self.entities):
                self.entities.append((entity, "DATE"))

    def get_entities(self):
        return self.entities

    def run_local_linguakit(self, text):
        temp_filename = "temp_processing_text.txt"
        with open(temp_filename, "w", encoding="utf-8") as f:
            f.write(text)
        executable = os.path.join(self.linguakit_path, "linguakit")
        command = [executable, "rel", "pt", temp_filename]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", check=True)
            return result.stdout.strip().split('\n')
        except Exception:
            return []
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def resolve_coreferences(self, raw_lines):
        initial_triples = []
        
        # Memory registers for context tracking (didnt work out that well)
        last_location = "Portugal"  
        last_continent = "Europa"
        last_organization = ""

        # Update fallbacks based on what SpaCy found first
        for ent, label in self.entities:
            if label == "LOC" and ent.lower() != "portugal":
                last_location = ent
                break

        # Step 1: Clean, parse and apply the coreference substitutions
        for line in raw_lines:
            if not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) < 4:
                continue
                
            subj = parts[1].strip().replace('@', ' ')
            rel = parts[2].strip().replace('@', ' ')
            obj = parts[3].strip().replace('@', ' ')

            for ent, label in self.entities:
                if ent.lower() in subj.lower() or ent.lower() in obj.lower():
                    if label == "LOC":
                        if any(c in ent.lower() for c in ["europa", "áfrica", "américa", "ásia", "oceania"]):
                            last_continent = ent
                        else:
                            last_location = ent
                    elif label == "ORG":
                        last_organization = ent

            s_low = subj.lower()
            if s_low in ["este país", "esta nação", "o país", "o território"]:
                subj = last_location
            elif s_low in ["este continente", "o continente"]:
                subj = last_continent
            elif s_low in ["o reino", "esta dinastia", "o império"]:
                subj = last_organization if last_organization else last_location
            elif s_low in ["esta", "ele", "ela"]:
                subj = last_location

            o_low = obj.lower()
            if o_low in ["este país", "esta nação", "o país", "o território"]:
                obj = last_location
            elif o_low in ["este continente", "o continente"]:
                obj = last_continent
            elif o_low in ["o reino", "esta dinastia", "o império"]:
                obj = last_organization if last_organization else last_location

            initial_triples.append({"subject": subj, "relation": rel, "object": obj})

        resolved_triples = []
        skip_indices = set()

        # Sort longer relations to the back so we can match sub-fragments progressively
        indexed_triples = list(enumerate(initial_triples))
        
        for i, t1 in indexed_triples:
            if i in skip_indices:
                continue
                
            merged_fact = t1.copy()
            
            for j, t2 in indexed_triples:
                if i == j or j in skip_indices:
                    continue
                
                # Check if they share the exact same subject
                if t1["subject"].lower() == t2["subject"].lower():
                    # Look for structural nesting
                    # If t2's relation incorporates t1's object and shorter relation string
                    r1, o1 = t1["relation"].lower(), t1["object"].lower()
                    r2, o2 = t2["relation"].lower(), t2["object"].lower()
                    
                    if (o1 in r2 and r1 in r2) or (o2 in r1 and r2 in r1):
                        # Construct a richer object structure by appending the missing segments
                        if len(r2) > len(r1):
                            # Clean and concatenate the floating modifier (like the missing 'tres part')
                            merged_fact["relation"] = t1["relation"]
                            # e.g., combining "uma bulla de Gregorio" + "1376"
                            if t2["object"] not in merged_fact["object"]:
                                merged_fact["object"] = f"{t1['object']} ({t2['object']})"
                        else:
                            merged_fact["relation"] = t2["relation"]
                            if t1["object"] not in merged_fact["object"]:
                                merged_fact["object"] = f"{t2['object']} ({t1['object']})"
                                
                        skip_indices.add(j)

            resolved_triples.append((merged_fact["subject"], merged_fact["relation"], merged_fact["object"]))
            
        return resolved_triples

    def prepare_relations(self, text):
        raw_lines = self.run_local_linguakit(text)
        self.relations = self.resolve_coreferences(raw_lines)

    def get_relations(self):
        return self.relations

    def save_knowledge_base(self, file_path="knowledge_base.txt"):
        """Saves both entities and triples into a highly structured, vertically aligned file."""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== ENTITIES ===\n")
            for ent, label in self.entities:
                f.write(f"{ent:<35} | {label}\n")
                
            f.write("\n=== TRIPLES ===\n")
            f.write(f"{'SUBJECT':<45} | {'RELATION':<40} | {'OBJECT'}\n")
            f.write(f"{'-'*45} | {'-'*40} | {'-'*30}\n")
            
            for subj, rel, obj in self.relations:
                s = " ".join(subj.split())
                r = " ".join(rel.split())
                o = " ".join(obj.split())
                f.write(f"{s:<45} | {r:<40} | {o}\n")
                
        print(f"🎉 Well-aligned Knowledge base successfully saved to: {file_path}")