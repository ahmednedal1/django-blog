from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    author = models.ForeignKey(
        'blog.User',
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
    )

    categories = models.ManyToManyField(
        'blog.Category',
        related_name='posts',
        blank=True,
    )

    def __str__(self):
        return self.title
