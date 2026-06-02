def count_words_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            
            # Split text into words based on whitespace
            words = text.split()
            
            return len(words)
    
    except FileNotFoundError:
        print("Error: File not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    file_path = input("Enter the path to the text file: ")
    word_count = count_words_in_file(file_path)
    
    if word_count is not None:
        print(f"Number of words: {word_count}")