from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import CategoryViewSet, CommentViewSet, PostViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register('categories', CategoryViewSet)
router.register('comments', CommentViewSet)

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('api/get-posts/', views.get_posts, name='get_posts'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
