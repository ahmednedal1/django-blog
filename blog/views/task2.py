from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

from ..models import Category, Comment, Post, User
from ..serializers import CategorySerializer, UserSerializer
from ..serializers.task2 import CreateCommentSerializer, CreatePostSerializer


class CreateEntityViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    # Task 2 is a public creation exercise, with no login prerequisite.
    permission_classes = (AllowAny,)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class UserCreateViewSet(CreateEntityViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryCreateViewSet(CreateEntityViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PostCreateViewSet(CreateEntityViewSet):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer


class CommentCreateViewSet(CreateEntityViewSet):
    queryset = Comment.objects.all()
    serializer_class = CreateCommentSerializer
