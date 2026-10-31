from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..models import Category
from ..serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
