from rest_framework.routers import SimpleRouter

from .views.task2 import (
    CategoryCreateViewSet,
    CommentCreateViewSet,
    PostCreateViewSet,
    UserCreateViewSet,
)

app_name = 'task2'

router = SimpleRouter()
router.register('users', UserCreateViewSet)
router.register('categories', CategoryCreateViewSet)
router.register('posts', PostCreateViewSet)
router.register('comments', CommentCreateViewSet)

urlpatterns = router.urls
