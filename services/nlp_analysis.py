import spacy
from wordfreq import word_frequency
import statistics

# Load the French language model in SpaCy
nlp = spacy.load("fr_core_news_md")

# Calculate Fluency Score
def calculate_fluency_score(wpm, min_wpm=30, max_wpm=160):
    score = max(0, min(100, ((wpm - min_wpm) / (max_wpm - min_wpm)) * 100))
    return round(score)

# Calculate Vocabulary Score based on unique lemmas and median frequency
def calculate_vocabulary_score(unique_lemmas, total_lemmas, median_frequency):
    unique_lemma_ratio = unique_lemmas / total_lemmas if total_lemmas > 0 else 0
    median_frequency_score = 1 - median_frequency  # Reward for less common words (lower frequency)
    score = (unique_lemma_ratio + median_frequency_score) / 2 * 100
    return round(score)

# Function to analyze lemmas, frequency, and calculate scores
def analyze_lemmas_and_frequency(paragraph, duration_in_minutes):
    doc = nlp(paragraph)
    lemmas = [token.lemma_ for token in doc if token.is_alpha]

    total_lemmas = len(lemmas)
    unique_lemmas = len(set(lemmas))
    frequencies = [word_frequency(lemma, 'fr', wordlist='best') for lemma in lemmas]

    median_frequency = statistics.median(frequencies) if frequencies else 1  # Use 1 if no frequencies

    # Calculate words per minute (WPM)
    total_words = len(lemmas)
    wpm = total_words / duration_in_minutes

    # Calculate Scores
    fluency_score = calculate_fluency_score(wpm)
    vocabulary_score = calculate_vocabulary_score(unique_lemmas, total_lemmas, median_frequency)

    return total_lemmas, unique_lemmas, median_frequency, fluency_score, vocabulary_score, wpm