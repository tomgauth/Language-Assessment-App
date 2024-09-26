from openai import OpenAI
import os
from dotenv import load_dotenv
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Load environment variables from .env
load_dotenv()

# Function to send transcription to ChatGPT and evaluate the naturalness
def evaluate_naturalness(transcription):
    # Define the prompt to instruct ChatGPT
    messages = [
        {"role": "system", "content": "You are a language expert. You will evaluate text for its natural and native-like conversational qualities."},
        {"role": "user", "content": f"Evaluate this text for naturalness and native-like quality: '{transcription}'. Provide a score from 0 to 100 and explain your evaluation."}
    ]

    # Send the prompt to the OpenAI API
    try:
        response = client.chat.completions.create(model="gpt-4",  # Or use 'gpt-3.5-turbo'
        messages=messages,
        temperature=0.5  # Adjust temperature for creativity vs. consistency
        )

        # Extract the content from the response
        feedback = response.choices[0].message.content
        return feedback

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"