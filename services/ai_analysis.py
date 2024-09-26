import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def evaluate_naturalness(transcription):
    messages = [
        {"role": "system", "content": "You are a language expert evaluating conversational text."},
        {"role": "user", "content": f"Evaluate this text for naturalness and native-like quality: '{transcription}'. Provide a score and feedback."}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use 'gpt-3.5-turbo' if needed
            messages=messages,
            temperature=0.5
        )
        feedback = response['choices'][0]['message']['content']
        return feedback

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"