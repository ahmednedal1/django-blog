from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..AI_Content.services import PostNotFoundError, summarize_post


# Task 3: translate service results and errors into HTTP responses.
@api_view(['POST'])
def summarize_post_view(request, post_id: int):
    try:
        result = summarize_post(post_id)
    except PostNotFoundError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as exc:
        return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(result, status=status.HTTP_200_OK)
