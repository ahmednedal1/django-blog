from typing import ClassVar

from rest_framework import serializers

from ..models import Category, Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'id',
            'title',
            'content',
            'created_date',
            'updated_date',
            'author',
            'categories',
        )
        read_only_fields = ('id', 'created_date', 'updated_date')


# Task 2: creation payload with a required singular category.
class CreatePostSerializer(serializers.ModelSerializer):
    # The task accepts one category; the existing model stores a category set.
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True,
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'category', 'created_date', 'updated_date')
        read_only_fields = ('id', 'created_date', 'updated_date')
        extra_kwargs: ClassVar[dict[str, dict[str, bool]]] = {
            'author': {'required': True, 'allow_null': False},
        }

    def create(self, validated_data):
        category = validated_data.pop('category')
        post = super().create(validated_data)
        post.categories.add(category)
        return post

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = instance.categories.order_by('pk').values_list('pk', flat=True).first()
        return data
