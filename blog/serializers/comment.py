from rest_framework import serializers

from ..models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'content', 'created_at', 'updated_at', 'author', 'post')
        read_only_fields = ('id', 'created_at', 'updated_at')


# Task 2: require author and post when creating comments.
class CreateCommentSerializer(CommentSerializer):
    class Meta(CommentSerializer.Meta):
        extra_kwargs = {
            'author': {'required': True, 'allow_null': False},
            'post': {'required': True, 'allow_null': False},
        }
