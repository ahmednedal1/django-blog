from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny


# Task 2: public POST creation, saved as one transaction.
class CreateEntityViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()
