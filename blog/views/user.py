from ..models import User
from ..serializers import UserSerializer
from .base import CreateEntityViewSet


# Task 2: blog author profile creation.
class UserCreateViewSet(CreateEntityViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

