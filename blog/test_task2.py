from unittest.mock import patch

from django.db import OperationalError
from rest_framework.test import APITestCase

from .models import Category, Comment, Post, User


class Task2CreateAPITests(APITestCase):
    def setUp(self):
        self.author = User.objects.create(username='writer', email='writer@example.com')
        self.category = Category.objects.create(name='Technology', description='Tech')
        self.post = Post.objects.create(title='Existing', content='Content', author=self.author)
        self.post.categories.add(self.category)
        self.cases = (
            ('users', User, {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'john', 'last_name': 'doe'}, ('username', 'email', 'first_name', 'last_name')),
            ('categories', Category, {'name': 'Science', 'description': 'Articles'}, ('name',)),
            ('posts', Post, {'title': 'Introduction', 'content': 'DRF APIs', 'author': self.author.pk, 'category': self.category.pk}, ('title', 'content', 'author', 'category')),
            ('comments', Comment, {'content': 'Great article!', 'author': self.author.pk, 'post': self.post.pk}, ('content', 'author', 'post')),
        )

    def test_all_four_exact_endpoints_create_records(self):
        for resource, model, payload, _ in self.cases:
            with self.subTest(resource=resource):
                before = model.objects.count()
                response = self.client.post(f'/api/{resource}/', payload, format='json')
                self.assertEqual(response.status_code, 201, response.data)
                self.assertEqual(model.objects.count(), before + 1)
                record = model.objects.get(pk=response.data['id'])
                for field, value in payload.items():
                    self.assertEqual(response.data[field], value)
                    if field == 'category':
                        self.assertEqual(list(record.categories.values_list('pk', flat=True)), [value])
                    else:
                        saved = getattr(record, field)
                        self.assertEqual(saved.pk if field in ('author', 'post') else saved, value)
                self.assertNotIn('password', response.data)

    def test_required_fields_reject_missing_blank_and_null(self):
        for resource, model, payload, required in self.cases:
            for field in required:
                for invalid in ('missing', '', None):
                    with self.subTest(resource=resource, field=field, invalid=invalid):
                        data = payload.copy()
                        if invalid == 'missing':
                            data.pop(field)
                        else:
                            data[field] = invalid
                        before = model.objects.count()
                        response = self.client.post(f'/api/{resource}/', data, format='json')
                        self.assertEqual(response.status_code, 400, response.data)
                        self.assertIn(field, response.data)
                        self.assertEqual(model.objects.count(), before)

    def test_duplicate_usernames_emails_and_categories(self):
        payload = self.cases[0][2]
        for data, field in (
            ({**payload, 'username': self.author.username}, 'username'),
            ({**payload, 'email': self.author.email}, 'email'),
            ({**payload, 'email': 'not-an-email'}, 'email'),
        ):
            response = self.client.post('/api/users/', data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertIn(field, response.data)
        response = self.client.post('/api/categories/', {'name': self.category.name, 'description': 'Duplicate'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.data)

    def test_invalid_relationship_ids(self):
        for resource, model, payload, _ in self.cases[2:]:
            fields = ('author', 'category') if resource == 'posts' else ('author', 'post')
            for field in fields:
                with self.subTest(resource=resource, field=field):
                    before = model.objects.count()
                    response = self.client.post(f'/api/{resource}/', {**payload, field: 999999}, format='json')
                    self.assertEqual(response.status_code, 400)
                    self.assertIn(field, response.data)
                    self.assertEqual(model.objects.count(), before)

    def test_post_and_category_link_are_atomic_on_server_failure(self):
        before = Post.objects.count()
        with patch('blog.serializers.task2.CreatePostSerializer.create') as create:
            def fail(validated_data):
                Post.objects.create(title='Must roll back', content='Content')
                raise OperationalError('Simulated database failure')
            create.side_effect = fail
            self.client.raise_request_exception = False
            response = self.client.post('/api/posts/', self.cases[2][2], format='json')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(Post.objects.count(), before)
