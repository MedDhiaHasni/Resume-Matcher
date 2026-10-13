"""
Core agent logic for the Resume ↔ Job Description Matcher.
Handles LLM calls, prompt construction, and mock mode.
"""
import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Model to use on Groq's free tier
MODEL_NAME = "openai/gpt-oss-120b"

def get_client():
    """Return a Groq client, or None if no API key is set (mock mode)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def build_prompt(resume_text: str, jd_text: str) -> str:
    """Build the prompt we send to the LLM."""
    return f"""You are an expert technical recruiter. Analyze the resume against the job description.

Return ONLY valid JSON with this exact structure:
{{
  "match_score": <integer 0-100>,
  "missing_skills": ["skill1", "skill2", ...],
  "matching_skills": ["skill1", "skill2", ...],
  "explanation": "<one short paragraph explaining the score>",
  "rewritten_bullets": ["improved bullet 1", "improved bullet 2", "improved bullet 3"]
}}

Rules:
- Be honest about the score. Don't inflate.
- "missing_skills" = skills the JD requires but the resume lacks.
- "matching_skills" = skills the resume has that the JD needs.
- "rewritten_bullets" = 3 resume bullet points rewritten to better target this JD.
- Return ONLY the JSON object. No markdown, no explanations outside the JSON.

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}
"""

def get_mock_response() -> dict:
    """Fallback response when no API key is set. Lets the app run without a key."""
    return {
        "match_score": 72,
        "missing_skills": ["Docker", "AWS", "Kubernetes"],
        "matching_skills": ["Python", "SQL", "Git", "REST APIs"],
        "explanation": "Strong overlap on core backend skills (Python, SQL, Git), but the resume doesn't show cloud or containerization experience that this role emphasizes. Consider adding any Docker/AWS exposure to close the gap.",
        "rewritten_bullets": [
            "Built and deployed REST APIs in Python serving 10k+ daily requests",
            "Optimized SQL queries reducing average response time by 40%",
            "Collaborated in an Agile team using Git for version control across 5 microservices"
        ]
    }

def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """Main entry point: returns analysis dict."""
    if not resume_text.strip() or not jd_text.strip():
        return {"error": "Both resume and job description must be provided."}

    client = get_client()
    if client is None:
        return get_mock_response()

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a JSON-only API. Always return valid JSON."},
                {"role": "user", "content": build_prompt(resume_text, jd_text)}
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        return {"error": f"LLM call failed: {str(e)}"}