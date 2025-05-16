from openai import OpenAI
import os

def dynamic_skills_analysis(
    text: str,
    skills: list,
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
        prompt = skill['prompt'].format(text=text)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a language assessment assistant. Always return a score (0-100) and a short feedback."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message.content.strip()
        # Try to extract score and feedback (simple regex or convention)
        import re
        score_match = re.search(r"score\s*[:=\-]?\s*(\d{1,3})", content, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None
        feedback = content
        results.append({
            "skill": skill['name'],
            "score": score,
            "feedback": feedback
        })
    return results
