import json
import re

def clean_and_parse_json(response_text: str) -> dict:
    """
    Cleans AI raw response text and parses it into a dictionary with 'subject' and 'body'.
    Raises ValueError if validation fails.
    """
    cleaned = response_text.strip()
    
    # 1. Strip markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    # 2. Attempt direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict) and "subject" in data and "body" in data:
            return data
    except Exception:
        pass

    # 3. Regex fallback: extract first match of anything between curly braces
    try:
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and "subject" in data and "body" in data:
                return data
    except Exception:
        pass

    raise ValueError("Invalid JSON format or missing required keys ('subject', 'body').")
