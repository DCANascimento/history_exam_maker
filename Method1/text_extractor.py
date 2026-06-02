import os

class TextExtractor:
    def __init__(self):
        self.target_folder = "../text_samples/"

    def get_text(self, file_name):
        file_path = os.path.join(self.target_folder, file_name)
        
        with open(file_path, "r", encoding="utf-8") as f:
            result = " ".join([line.strip() for line in f.readlines() if line.strip()])
            
        return result
