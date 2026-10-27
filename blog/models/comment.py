from django.db import models


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        'blog.User',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True,
    )
    post = models.ForeignKey(
        'blog.Post',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.content[:50]
