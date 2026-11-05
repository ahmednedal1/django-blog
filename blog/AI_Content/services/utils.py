from django.conf import settings

from ..client import ContentClient


def validate_text_input(text: str, min_length: int = 20, field_name: str = "Content") -> str:
    """Reject empty/whitespace/too-short input; return the cleaned text."""
    if not text or not text.strip():
        raise ValueError(f"{field_name} cannot be empty or whitespace.")

    cleaned_text = text.strip()

    if len(cleaned_text) < min_length:
        raise ValueError(f"{field_name} must be at least {min_length} characters long.")

    return cleaned_text

def validate_title(title: str, min_length: int = 5) -> str:
    """Title validation is just text validation with a shorter minimum."""
    return validate_text_input(title, min_length, field_name="Title")

def generate_ai_content(prompt: str, system: str | None = None) -> str:
    client = ContentClient(
        api_key=settings.OPENAI_APIKEY,
        model=settings.OPENAI_MODEL,
    )
    result = client.generate_content(prompt, system=system)
    if not isinstance(result, str) or not result.strip():
        raise ValueError("Model output was empty or invalid.")

    return result.strip()
