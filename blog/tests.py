from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .models import Category, Comment, User


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

    def test_models_have_no_relationships(self):
        for model in (User, Category, Comment):
            with self.subTest(model=model.__name__):
                self.assertFalse(any(field.is_relation for field in model._meta.get_fields()))
