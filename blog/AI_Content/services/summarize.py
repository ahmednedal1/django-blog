from django.conf import settings

from ...models import Post
from ..client import ContentClient


class PostNotFoundError(ValueError):
    """A valid post ID did not match a stored post."""


def _build_summary_prompt(content: str) -> str:
    return (
        "Summarize the following blog post accurately and concisely in at most "
        "500 characters. Return only the summary.\n\n"
        f"Blog post:\n{content}"
    )


# Task 3: retrieve the saved post and summarize it through the shared client.
def summarize_post(post_id: int) -> dict:
    if isinstance(post_id, bool) or not isinstance(post_id, int) or post_id <= 0:
        raise ValueError('Post ID must be a positive integer.')

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist as exc:
        raise PostNotFoundError(f'Post {post_id} was not found.') from exc

    if not post.content or not post.content.strip():
        raise ValueError('Post content cannot be empty or whitespace.')

    client = ContentClient(api_key=settings.OPENAI_APIKEY, model=settings.OPENAI_MODEL)
    summary = client.generate(_build_summary_prompt(post.content))
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError('The generated summary is empty.')

    # Keep the response within the assignment's hard limit even if the model exceeds it.
    summary = summary.strip()[:500].rstrip()
    return {
        'post_id': post.pk,
        'title': post.title,
        'summary': summary,
        'length': len(summary),
    }
