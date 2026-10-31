from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..models import Post
from ..serializers import PostSerializer


class PostPagination(PageNumberPagination):
    page_size = 10


class PostViewSet(viewsets.ModelViewSet):
    queryset = (
        Post.objects.select_related('author')
        .prefetch_related('categories')
        .order_by('-created_date', '-pk')
    )
    serializer_class = PostSerializer
    pagination_class = PostPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)


@api_view(['GET'])
def get_posts(request):
    try:
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        if page < 1 or limit < 1:
            raise ValueError
        start = (page - 1) * limit
        end = start + limit

        posts = Post.objects.filter(categories__name__iexact='AI').order_by('pk')[start:end]
        serializer = PostSerializer(posts, many=True)
        return Response(
            {'posts': serializer.data, 'page': page, 'limit': limit}
        )
    except ValueError:
        return Response(
            {'error': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def post_list(request):
    posts = (
        Post.objects.select_related('author')
        .prefetch_related('categories')
        .order_by('-created_date', '-pk')
    )
    return render(request, 'blog/post_list.html', {'posts': posts})
