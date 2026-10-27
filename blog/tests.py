from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import Category, Comment, Post, User


class BlogModelTests(TestCase):
    def test_user_creation(self):
        before = timezone.now()
        user = User.objects.create(
            username='ahmed',
            email='ahmed@example.com',
            first_name='Ahmed',
            last_name='Ali',
        )
        user.refresh_from_db()
        self.assertEqual(str(user), 'ahmed')
        self.assertEqual(user.first_name, 'Ahmed')
        self.assertEqual(user.last_name, 'Ali')
        self.assertGreaterEqual(user.created_at, before)
        self.assertLessEqual(user.created_at, timezone.now())

    def test_username_and_email_are_unique(self):
        User.objects.create(username='ahmed', email='ahmed@example.com')
        for username, email in [
            ('ahmed', 'another@example.com'),
            ('another', 'ahmed@example.com'),
        ]:
            with self.subTest(username=username, email=email):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    User.objects.create(username=username, email=email)

    def test_category_creation(self):
        before = timezone.now()
        category = Category.objects.create(name='Django', description='Django posts')
        category.refresh_from_db()
        self.assertEqual(str(category), 'Django')
        self.assertEqual(category.description, 'Django posts')
        self.assertGreaterEqual(category.created_at, before)
        self.assertLessEqual(category.created_at, timezone.now())

    def test_category_name_is_unique(self):
        Category.objects.create(name='Django', description='Django posts')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Category.objects.create(name='Django', description='Duplicate')

    def test_comment_timestamps(self):
        before = timezone.now()
        comment = Comment.objects.create(content='A useful post!')
        comment.refresh_from_db()
        created_at = comment.created_at
        self.assertEqual(str(comment), 'A useful post!')
        self.assertGreaterEqual(created_at, before)
        self.assertGreaterEqual(comment.updated_at, created_at)
        self.assertLessEqual(comment.updated_at, timezone.now())

        previous_update = before - timedelta(days=1)
        Comment.objects.filter(pk=comment.pk).update(updated_at=previous_update)
        comment.content = 'Updated comment'
        comment.save()
        comment.refresh_from_db()
        self.assertEqual(comment.created_at, created_at)
        self.assertGreater(comment.updated_at, previous_update)
        self.assertEqual(str(comment), 'Updated comment')

    def test_models_have_no_forward_relationships(self):
        for model in (User, Category):
            with self.subTest(model=model.__name__):
                self.assertFalse(any(field.is_relation for field in model._meta.fields))

    def test_author_can_have_multiple_posts(self):
        author = User.objects.create(username='writer', email='writer@example.com')
        first = Post.objects.create(title='First post', content='First', author=author)
        second = Post.objects.create(title='Second post', content='Second', author=author)
        first.refresh_from_db()
        self.assertEqual(first.author, author)
        self.assertCountEqual(author.posts.all(), [first, second])

    def test_deleting_author_deletes_post(self):
        author = User.objects.create(username='writer', email='writer@example.com')
        post = Post.objects.create(title='A post', content='Content', author=author)
        author.delete()
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_post_can_have_no_author(self):
        post = Post.objects.create(title='An existing post', content='Content')
        post.refresh_from_db()
        self.assertIsNone(post.author)

    def test_category_can_have_multiple_posts(self):
        category = Category.objects.create(name='Python', description='Python posts')
        first = Post.objects.create(title='First', content='First')
        second = Post.objects.create(title='Second', content='Second')
        first.categories.add(category)
        second.categories.add(category)
        self.assertCountEqual(first.categories.all(), [category])
        self.assertCountEqual(category.posts.all(), [first, second])

    def test_deleting_category_preserves_post(self):
        category = Category.objects.create(name='Python', description='Python posts')
        post = Post.objects.create(title='A post', content='Content')
        post.categories.add(category)
        category.delete()
        post.refresh_from_db()
        self.assertFalse(post.categories.exists())

    def test_post_can_have_no_category(self):
        post = Post.objects.create(title='An existing post', content='Content')
        post.refresh_from_db()
        self.assertFalse(post.categories.exists())

    def test_post_can_have_multiple_categories(self):
        python = Category.objects.create(name='Python', description='Python posts')
        django = Category.objects.create(name='Django', description='Django posts')
        post = Post.objects.create(title='A post', content='Content')
        post.categories.add(python, django)
        self.assertCountEqual(post.categories.all(), [python, django])
        post.categories.remove(python)
        self.assertCountEqual(post.categories.all(), [django])
        self.assertTrue(Category.objects.filter(pk=python.pk).exists())

    def test_user_and_post_can_have_multiple_comments(self):
        author = User.objects.create(username='reader', email='reader@example.com')
        post = Post.objects.create(title='A post', content='Content')
        first = Comment.objects.create(content='First', author=author, post=post)
        second = Comment.objects.create(content='Second', author=author, post=post)
        first.refresh_from_db()
        self.assertEqual(first.author, author)
        self.assertEqual(first.post, post)
        self.assertCountEqual(author.comments.all(), [first, second])
        self.assertCountEqual(post.comments.all(), [first, second])

    def test_deleting_comment_author_deletes_comment_but_preserves_other_post(self):
        author = User.objects.create(username='reader', email='reader@example.com')
        post = Post.objects.create(title='A post', content='Content')
        comment = Comment.objects.create(content='Comment', author=author, post=post)
        author.delete()
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())

    def test_deleting_post_deletes_its_comments_only(self):
        post = Post.objects.create(title='A post', content='Content')
        comment = Comment.objects.create(content='Comment', post=post)
        other = Comment.objects.create(content='Unassigned')
        post.delete()
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertTrue(Comment.objects.filter(pk=other.pk).exists())

    def test_comment_can_have_no_author_or_post(self):
        comment = Comment.objects.create(content='Existing comment')
        comment.refresh_from_db()
        self.assertIsNone(comment.author)
        self.assertIsNone(comment.post)

    def test_deleting_post_author_cascades_to_comments(self):
        author = User.objects.create(username='writer', email='writer@example.com')
        post = Post.objects.create(title='A post', content='Content', author=author)
        comment = Comment.objects.create(content='Comment', post=post)
        author.delete()
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
