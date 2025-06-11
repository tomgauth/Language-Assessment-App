from openai import OpenAI
import os
import streamlit as st
def dynamic_skills_analysis(
    text: str,
    skills: list,
    audio_duration: str,
    question: str,
    context: str,
    openai_api_key: str = None,
    model: str = "gpt-3.5-turbo"
):
    """
    Args:
        text: The user's answer to analyze.
        skills: List of dicts, each with:
            - 'name': Skill name
            - 'prompt': Prompt template (with {text} placeholder)
        openai_api_key: Your OpenAI API key (optional, will use env if not provided).
        model: OpenAI model to use.
    Returns:
        List of dicts: [{'skill': ..., 'score': ..., 'feedback': ...}, ...]
    """
    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    results = []
    for skill in skills:
        prompt = skill['prompt'] + "| Transcription: " + text + "| Audio Duration: " + audio_duration + "| Question: " + question + "| Context: " + context
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": """You are a language assessment assistant. Always return a score (0-100) and a short feedback.
                 - At the end, provide the total score formatted as "TOTAL_SCORE:[total_score]" with a 2 or 3 digit integer in the square brackets."""
                 },
                {"role": "system", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        # Try to extract score and feedback (simple regex or convention)
        import re
        score_match = re.search(r"score\s*[:=\-]?\s*(\d{1,3})", content, re.IGNORECASE)
        if not score_match:
            score_match = re.search(r"\b(\d{2}|100)\b", content)
        score = int(score_match.group(1)) if score_match else 0
        score = max(0, min(score, 100))  # Ensure score is between 0 and 100
        feedback = content
        results.append({
            "skill": skill['name'],
            "score": score,
            "feedback": feedback
        })
    return results
