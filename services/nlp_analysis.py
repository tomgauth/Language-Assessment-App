import spacy
from wordfreq import word_frequency
import statistics

# Load the French language model in SpaCy
nlp = spacy.load("fr_core_news_md")

# Function to calculate fluency score based on WPM
def calculate_fluency_score(wpm):
    max_wpm = 160  # Native speaker fluency at 100%
    min_wpm = 30   # Baseline for low fluency
    score = max(0, min(100, ((wpm - min_wpm) / (max_wpm - min_wpm)) * 100))
    return score

# Function to calculate vocabulary score based on median word frequency
def calculate_vocabulary_score(median_frequency):
    native_median = 0.001  # Native speaker's median frequency
    low_vocab_median = 0.01  # Higher value means simpler words
    score = max(0, min(100, ((low_vocab_median - median_frequency) / (low_vocab_median - native_median)) * 100))
    return score

# Function to analyze lemmas, frequency, and calculate scores
def analyze_lemmas_and_frequency(paragraph, duration_in_minutes):
    # Process the text with SpaCy
    doc = nlp(paragraph)
    
    # Get lemmas for all tokens that are not punctuation
    lemmas = [token.lemma_ for token in doc if token.is_alpha]
    
    # Calculate total and unique lemmas
    total_lemmas = len(lemmas)
    unique_lemmas = len(set(lemmas))
    
    # Calculate word frequencies using wordfreq library
    frequencies = [word_frequency(lemma, 'fr', wordlist='best') for lemma in lemmas]
    
    # Calculate the median frequency of the words
    median_frequency = statistics.median(frequencies) if frequencies else 0
    
    # Calculate words per minute
    total_words = len(lemmas)
    wpm = total_words / duration_in_minutes
    
    # Calculate fluency and vocabulary scores
    fluency_score = calculate_fluency_score(wpm)
    vocabulary_score = calculate_vocabulary_score(median_frequency)
    
    return total_lemmas, unique_lemmas, median_frequency, fluency_score, vocabulary_score