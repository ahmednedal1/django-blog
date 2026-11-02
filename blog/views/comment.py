from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Comment
from ..serializers import CreateCommentSerializer, CommentSerializer
from .base import CreateEntityViewSet


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'post').order_by('-created_at', '-pk')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


# Task 2: POST-only creation endpoint.
class CommentCreateViewSet(CreateEntityViewSet):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
