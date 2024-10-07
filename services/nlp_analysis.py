import statistics
from collections import Counter
import streamlit as st

# Calculate Fluency Score based on words per minute (WPM)
def calculate_fluency_score(wpm, min_wpm=30, max_wpm=160):
    return round(max(0, min(100, ((wpm - min_wpm) / (max_wpm - min_wpm)) * 100)))

# Vocabulary Richness Calculation based on lemmas, word length, and POS diversity
def calculate_vocabulary_richness(unique_lemmas, total_lemmas, avg_word_length):
    unique_lemma_ratio = unique_lemmas / total_lemmas if total_lemmas > 0 else 0
    score = (unique_lemma_ratio + (avg_word_length / 5)) / 2 * 100  # Average score from lemma ratio and word length
    return round(score)

# General Text Analysis (without relying on any specific language models)
def analyze_lemmas_and_frequency(paragraph, duration_in_minutes):
    st.write("Performing general text analysis")

    # Tokenize by splitting the paragraph into words (basic tokenization)
    words = [word for word in paragraph.split() if word.isalpha()]
    
    total_lemmas = len(words)
    unique_lemmas = len(set(words))
    avg_word_length = sum(len(word) for word in words) / total_lemmas if total_lemmas > 0 else 0

    # Simple WPM calculation
    wpm = total_lemmas / duration_in_minutes if duration_in_minutes > 0 else 0

    # Calculate Scores
    fluency_score = calculate_fluency_score(wpm)
    vocabulary_richness_score = calculate_vocabulary_richness(unique_lemmas, total_lemmas, avg_word_length)

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

