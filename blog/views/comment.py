from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Comment
from ..serializers import CommentSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'post').order_by('-created_at', '-pk')
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
