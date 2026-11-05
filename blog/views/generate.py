from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..AI_Content.services import _generate_post


@api_view(["POST"])
def generate_post(request):
    title = request.data["title"]
    tone = request.data["tone"]

    try:
        result = _generate_post(title, tone)
        return Response(result, status=status.HTTP_200_OK)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
