import streamlit as st
from dotenv import load_dotenv
from services.text_analysis import analyze_text  # Import the service
from services.test_data import get_A2_sample_text   # Import the test sample text
from services.nlp_analysis import analyze_lemmas_and_frequency  # Import the function from nlp_analysis.py
from services.ai_analysis import evaluate_naturalness  # Import the new AI evaluation function
import os


default_text = get_A2_sample_text()

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Use the API key in your code
print(f"Your OpenAI API key is: {openai_api_key}")

if st.button("Click here if you're a pookie"):
    st.title("Who is a pookie curiosa❤️🐹?")

st.write("This app will assess your French language skills.")

# Streamlit app layout
st.title("French Language Assessment - Text Analysis")

# Input for the user to input the duration in minutes
duration_in_minutes = st.number_input("Enter the duration of speech (in minutes)", min_value=1.0, step=0.1)

# Text input area for the user to input a paragraph (up to 300+ words)
paragraph = st.text_area("Enter a paragraph (up to 300 words):",value=default_text, height=200)

# Button to trigger the analysis
if st.button("Analyze Text"):
    # Check if the input is not empty
    if paragraph:
        # Call the function to analyze lemmas, frequency, and calculate fluency/vocabulary scores
        total_lemmas, unique_lemmas, median_frequency, fluency_score, vocabulary_score = analyze_lemmas_and_frequency(paragraph, duration_in_minutes)
        feedback = evaluate_naturalness(paragraph)
        # Display the results
        st.write(f"Total number of lemmas: {total_lemmas}")
        st.write(f"Number of unique lemmas: {unique_lemmas}")
        st.write(f"Median frequency of words: {median_frequency}")
        st.write(f"Fluency Score (Words Per Minute): {fluency_score}%")
        st.write(f"Vocabulary Score (Median Word Frequency): {vocabulary_score}%")
        st.write("AI's evaluation:")
        st.write(feedback)
    else:
        st.warning("Please enter a paragraph before analyzing.")


