from rest_framework import serializers

from ..models import Category, Post
from .comment import CommentSerializer


class CreatePostSerializer(serializers.ModelSerializer):
    # The task accepts one category; the existing model stores a category set.
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), write_only=True,
    )

    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'category', 'created_date', 'updated_date')
        read_only_fields = ('id', 'created_date', 'updated_date')
        extra_kwargs = {'author': {'required': True, 'allow_null': False}}

    def create(self, validated_data):
        category = validated_data.pop('category')
        post = super().create(validated_data)
        post.categories.add(category)
        return post

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['category'] = instance.categories.order_by('pk').values_list('pk', flat=True).first()
        return data


class CreateCommentSerializer(CommentSerializer):
    class Meta(CommentSerializer.Meta):
        extra_kwargs = {
            'author': {'required': True, 'allow_null': False},
            'post': {'required': True, 'allow_null': False},
        }
