import statistics
from collections import Counter
import streamlit as st

# Simplified the shit out of this because why make it complicated?
def calculate_fluency_score(wpm, max_wpm=120):
    # Calculate score based on a simple linear relation up to 120 WPM
    return round(min(100, (wpm / max_wpm) * 100))

# Vocabulary Richness Calculation based on lemmas, word length, and POS diversity
# def calculate_vocabulary_richness(unique_lemmas, total_lemmas, avg_word_length):
  #  unique_lemma_ratio = unique_lemmas / total_lemmas if total_lemmas > 0 else 0
  #  score = (unique_lemma_ratio + (avg_word_length / 5)) / 2 * 100  # Average score from lemma ratio and word length
  # return round(score)

def calculate_vocabulary_richness(text):

    """
    This function evaluates the vocabulary richness of a given text by calculating a score from 0 to 100.
    It assesses two main components:
    
    1. Total Word Count: The number of words in the input text, with an expected minimum of 120 words.
    2. Unique Words Ratio: The proportion of words that appear only once in the text, with an expected ratio of 50%.
    
    The function calculates two sub-scores:
    - A word count score out of 50, based on the proportion of the total words relative to the expected 120 words.
    - A uniqueness score out of 50, based on the ratio of unique words compared to the expected 50%.
    
    The final score is the sum of these two sub-scores, capped at 100.

    Parameters:
    text (str): The input text to evaluate.

    Returns:
    dict: A dictionary containing the total word count, unique word count, unique word ratio, 
          and the final vocabulary richness score out of 100.
    """

    words = text.lower().split()
    
    # Total words spoken
    total_words = len(words)
    
    # Count the occurrences of each word
    from collections import Counter
    word_counts = Counter(words)
    
    # Count the number of unique words (words used only once)
    unique_words = sum(1 for count in word_counts.values() if count == 1)
    
    # Expected values
    expected_total_words = 120
    expected_unique_words_ratio = 0.5
    
    # Calculate the ratio of unique words in the text
    actual_unique_words_ratio = unique_words / total_words if total_words > 0 else 0
    
    # Calculate scores
    word_count_score = min(total_words / expected_total_words, 1) * 50
    uniqueness_score = min(actual_unique_words_ratio / expected_unique_words_ratio, 1) * 50
    
    # Total score out of 100
    total_score = word_count_score + uniqueness_score

    full_results = {
        "total_words": total_words,
        "unique_words": unique_words,
        "unique_words_ratio": actual_unique_words_ratio,
        "score": round(total_score, 2)
    }
    
    return round(total_score, 2) # let's keep it simple



# General Text Analysis (without relying on any specific language models)
def analyze_lemmas_and_frequency(transcription, duration_in_minutes):
    st.write("Performing general text analysis")

    paragraph = transcription.text
    # Tokenize by splitting the paragraph into words (basic tokenization)
    words = [word for word in paragraph.split() if word.isalpha()]
    
    total_lemmas = len(words)
    unique_lemmas = len(set(words))
    avg_word_length = sum(len(word) for word in words) / total_lemmas if total_lemmas > 0 else 0

    # Simple WPM calculation
    wpm = total_lemmas / duration_in_minutes if duration_in_minutes > 0 else 0

    # Calculate Scores
    fluency_score = calculate_fluency_score(wpm)
    # TODO: next function is dupplicating code
    vocabulary_richness_score = calculate_vocabulary_richness(paragraph)

    return {
        'total_lemmas': total_lemmas,
        'unique_lemmas': unique_lemmas,
        'avg_word_length': avg_word_length,
        'fluency_score': fluency_score,
        'vocabulary_score': vocabulary_richness_score,
        'wpm': wpm
    }

# Function to display the results in a table
def display_data_table(vocabulary_score, total_lemmas, unique_lemmas, avg_word_length, fluency_score, wpm):
    st.write("## Detailed Data Table")
    
    # Round all numeric values to integers
    data = {
        "Metric": ["Vocabulary Score", "Total Lemmas", "Unique Lemmas", "Average Word Length", "Fluency Score (WPM)", "Words per Minute"],
        "Value": [
            round(vocabulary_score), 
            round(total_lemmas), 
            round(unique_lemmas), 
            round(avg_word_length, 2),  # Show two decimal places for avg word length
            round(fluency_score), 
            round(wpm)
        ]
    }
    st.table(data)

