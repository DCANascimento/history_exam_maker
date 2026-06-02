import re

def remove_bracketed_content(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Remove anything inside square brackets (including the brackets)
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

# Example usage
input_path = 'example2.txt'
output_path = 'example2.txt'

remove_bracketed_content(input_path, output_path)