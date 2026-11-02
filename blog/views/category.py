from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Category
from ..serializers import CategorySerializer
from .base import CreateEntityViewSet


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


# Task 2: POST-only creation endpoint.
class CategoryCreateViewSet(CreateEntityViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
