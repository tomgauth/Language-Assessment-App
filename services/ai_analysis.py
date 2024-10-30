import openai
import os
from dotenv import load_dotenv
import streamlit as st
import re


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)


def evaluate_score(prompts, transcription):
    """
    Evaluates a language score based on the provided prompts and transcription,
    returning both a detailed evaluation and a total score.

    Parameters:
    - prompts: The prompt or system/user prompts to be evaluated.
    - transcription: The text transcription to be evaluated.

    Returns:
    - evaluation: Detailed evaluation as a string, containing each criterion's score and comments.
    - total_score: The total score as an integer between 0 and 100.
    """

    # Check if transcription is valid
    if not transcription:
        st.write("Error: Transcription is empty or None.")
        return "", 0
    
    # Inject the transcription into the prompts
    for i, prompt in enumerate(prompts):
        if '{transcription}' in prompt['content']:
            prompt['content'] = prompt['content'].format(transcription=transcription)
            print(f"Debug: Prompt {i} after injecting transcription: {prompt['content']}")
    
    print(f"Debug: Final prompts passed to API: {prompts}")

    try:
        # Call the OpenAI chat completion API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=prompts
        )
        
        print(f"Debug: API response received: {response}")
        
        # Extract the content from the response
        content = response.choices[0].message.content
        print(f"Debug: Content extracted from API response: {content}")

        # Separate the evaluation details and total score
        try:
            # Define the regex to capture total score as an integer
            score_regex = r"(?i)total[_\s]*score[:=\s]*[\[\(]?\s*(\d{1,3})\s*[%/\]]?"

            # Search for total score using regex
            match = re.search(score_regex, content)
            
            if match:
                # Extract the score as an integer
                total_score = int(match.group(1))
            else:
                print("Error: Could not find a valid score in the expected format. Setting score to 0.")
                total_score = 0

            # Assume the rest of the content before "TOTAL_SCORE" is the evaluation part
            evaluation_part = content.strip()

        except (ValueError, IndexError) as e:
            print(f"Error parsing evaluation or total score: {str(e)}")
            evaluation_part = content
            total_score = 0
            
            # Ensure the total score is within the valid range
            if not 0 <= total_score <= 100:
                print("Error: Total score is not within the valid range (0-100). Setting it to 0.")
                total_score = 0


        # Debug: Confirm parsed evaluation and total score
        print(f"Debug: Parsed evaluation: {evaluation_part}")
        print(f"Debug: Parsed total score: {total_score}")
        
        return evaluation_part, total_score

    except openai.OpenAIError as e:
        print(f"An error occurred while communicating with OpenAI: {str(e)}")
        return "", 0
    
    

# Define your prompt templates with placeholders for transcription
syntax_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
    {"role": "user", "content": """
    Evaluate the syntactic coherence of the following text and rate it from 0 to 100. Provide the evaluation in two parts:
    
    Part 1: Detailed Evaluation
    - List each of the following criteria with scores out of 20 and a brief comment:
        1. Conjugation: /20 - (Is verb conjugation correct and consistent?)
        2. Syntax: /20 - (Are sentences well-structured and syntactically correct?)
        3. Sentence Length: /20 - (Are sentence lengths varied and appropriate for fluency?)
        4. Correctness: /20 - (Are there grammar or word choice issues?)
        5. Fanciness: /20 - (Does the response include connectors and complex structures?)

    Part 2: Total Score
    - At the end, provide the total score formatted as "TOTAL_SCORE:[total_score]" with a 2 or 3 digit integer in the square brackets.
    
    Here is the transcription to evaluate: '{transcription}'."""}
]

communication_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
    {"role": "user", "content": """
    Evaluate the naturalness and communication style of the following text and rate it from 0 to 100. Provide the evaluation in two parts:

    Part 1: Detailed Evaluation
    - List each of the following criteria with scores out of 20 and a brief comment:
        1. Use of Fillers: /20 - (Are fillers like 'um', 'uh' used naturally?)
        2. Slang and Idioms: /20 - (Is natural-sounding slang or idiomatic language used?)
        3. Fluency: /20 - (Is the conversation smooth and uninterrupted?)
        4. Interactivity: /20 - (Is the response engaging, with back-and-forth interaction?)
        5. Storytelling and Humor: /20 - (Does the response have a natural flow, humor, or casual storytelling?)

    Part 2: Total Score
    - At the end, provide the total score formatted as "TOTAL_SCORE:[total_score]" with a 2 or 3 digit integer in the square brackets.
    
    Here is the transcription to evaluate: '{transcription}'."""}
]

naturalness_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language, focusing on how naturally they speak the language in a casual context."},
    {"role": "user", "content": """
    Evaluate the naturalness of the following transcription, focusing on how closely it resembles native speaker language in casual conversation. Provide the evaluation in two parts:

    Part 1: Detailed Evaluation
    - List each of the following criteria with scores out of 20 and a brief comment:
        1. Use of Idioms and Expressions: /20 - (Is idiomatic language used effectively?)
        2. Sentence Construction: /20 - (Is there variety in sentence structure, including informal styles?)
        3. Fillers and Hesitations: /20 - (Are fillers and natural pauses present as they would be in casual speech?)
        4. Flow and Rhythm of Speech: /20 - (Does the transcription flow like conversational speech?)
        5. Overall Naturalness: /20 - (Does the speaker sound like a native in casual conversation?)

    Part 2: Total Score
    - At the end, provide the total score formatted as "TOTAL_SCORE:[total_score]" with a 2 or 3 digit integer in the square brackets.
    
    Here is the transcription to evaluate: '{transcription}'."""}
]

# TODO: create a prompt that takes the initial question and assess how accurate the answer is. It can be considered as a comprehension test
accuracy_score_template = []

def evaluate_syntax(transcription):
    syntax_eval, syntax_score = evaluate_score(syntax_score_template, transcription)
    print("syntax_score: ", syntax_score)
    return syntax_eval, syntax_score

def evaluate_communication(transcription):
    com_eval, com_score = evaluate_score(communication_score_template, transcription)
    print("com_score: ", com_score)
    return com_eval, com_score

def evaluate_naturalness(transcription):
    naturalness_eval, naturalness_score = evaluate_score(naturalness_score_template, transcription)
    print("naturalness_score: ", naturalness_score)
    return naturalness_eval, naturalness_score