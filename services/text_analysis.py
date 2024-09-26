def analyze_text(paragraph):
    words = paragraph.split()  # Split text by spaces
    total_words = len(words)  # Count total words
    unique_words = len(set(words))  # Count unique words
    return total_words, unique_words