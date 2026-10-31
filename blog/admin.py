from django.contrib import admin

from .models import Category, Comment, Post, User


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_date', 'updated_date')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_date', 'updated_date', 'categories')
    ordering = ('-created_date',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'content', 'created_at')
    search_fields = ('post__title', 'author__username', 'content')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

    