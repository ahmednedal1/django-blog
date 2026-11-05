import logging

from .utils import generate_ai_content, validate_title

logger = logging.getLogger(__name__)


def _build_generate_prompt(title: str, tone: str | None = None) -> str:
    prompt = f"Write a short blog post about {title}"

    if tone:
        prompt += f"\nWrite it in a {tone} tone."

    prompt += "\nKeep the total output under 120 characters."
    return prompt


def _generate_post(title: str, tone: str | None = None) -> dict:
    cleaned_title = validate_title(title, min_length=5)
    prompt = _build_generate_prompt(cleaned_title, tone)

    try:
        cleaned_content = generate_ai_content(prompt)
    except ValueError as e:
        logger.error("Error generating content: %s", e)
        raise

    if len(cleaned_content) > 120:
        raise ValueError("Generated content exceeds 120 characters.")

    return {
        "title": cleaned_title,
        "content": cleaned_content,
        "tone": tone
    }
