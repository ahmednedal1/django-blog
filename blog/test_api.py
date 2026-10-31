from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Comment, Post, User


class BlogAPITests(APITestCase):
    def test_manual_posts_pagination(self):
        category = Category.objects.create(name='AI', description='AI posts')
        posts = [Post.objects.create(title=f'AI {i}', content='Content') for i in range(3)]
        for post in posts:
            post.categories.add(category)
        url = reverse('get_posts')
        first = self.client.get(url, {'limit': 2})
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(set(first.data), {'posts', 'page', 'limit'})
        self.assertEqual([item['id'] for item in first.data['posts']], [p.pk for p in posts[:2]])
        second = self.client.get(url, {'page': 2, 'limit': 2})
        self.assertEqual([item['id'] for item in second.data['posts']], [posts[2].pk])
        self.assertEqual(second.data['page'], 2)
        for parameter in ('page', 'limit'):
            for value in ('abc', '0', '-1', '1.5'):
                response = self.client.get(url, {parameter: value})
                self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
                self.assertEqual(response.data, {'error': 'An unexpected error occurred.'})
        self.assertEqual(self.client.post(url, {}, format='json').status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_manual_pagination_empty_results(self):
        response = self.client.get(reverse('get_posts'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'posts': [], 'page': 1, 'limit': 10})

    def test_posts_pagination(self):
        Post.objects.bulk_create([
            Post(title=f'Post {index}', content='Content')
            for index in range(11)
        ])
        expected_ids = list(
            Post.objects.order_by('-created_date', '-pk').values_list('pk', flat=True)
        )
        url = reverse('post-list')
        first = self.client.get(url)
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['count'], 12)
        self.assertIsNone(first.data['previous'])
        self.assertIsNotNone(first.data['next'])
        self.assertEqual([item['id'] for item in first.data['results']], expected_ids[:10])
        second = self.client.get(url, {'page': 2})
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertIsNone(second.data['next'])
        self.assertIsNotNone(second.data['previous'])
        self.assertEqual([item['id'] for item in second.data['results']], expected_ids[10:])
        self.assertEqual(self.client.get(url, {'page': 3}).status_code, status.HTTP_404_NOT_FOUND)

    def setUp(self):
        self.login_user = get_user_model().objects.create_user(username='api_editor')
        self.author = User.objects.create(username='writer', email='writer@example.com')
        self.category = Category.objects.create(name='Python', description='Python posts')
        self.post = Post.objects.create(title='First', content='Content', author=self.author)
        self.post.categories.add(self.category)
        self.comment = Comment.objects.create(content='Comment', author=self.author, post=self.post)

    def test_public_reads_and_protected_writes(self):
        for resource, record, payload in (
            ('post', self.post, {'title': 'New', 'content': 'Content'}),
            ('category', self.category, {'name': 'New', 'description': 'Description'}),
            ('comment', self.comment, {'content': 'New'}),
        ):
            with self.subTest(resource=resource):
                collection = reverse(f'{resource}-list')
                detail = reverse(f'{resource}-detail', args=[record.pk])
                self.assertEqual(self.client.get(collection).status_code, status.HTTP_200_OK)
                self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
                self.assertEqual(self.client.post(collection, payload, format='json').status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(self.client.patch(detail, payload, format='json').status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(self.client.delete(detail).status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_crud_for_each_resource(self):
        self.client.force_authenticate(self.login_user)
        for resource, model, payload, update in (
            ('post', Post, {'title': 'New', 'content': 'Content', 'author': self.author.pk, 'categories': [self.category.pk]}, {'title': 'Updated'}),
            ('category', Category, {'name': 'New', 'description': 'Description'}, {'name': 'Updated'}),
            ('comment', Comment, {'content': 'New', 'author': self.author.pk, 'post': self.post.pk}, {'content': 'Updated'}),
        ):
            with self.subTest(resource=resource):
                response = self.client.post(reverse(f'{resource}-list'), payload, format='json')
                self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
                record_id = response.data['id']
                detail = reverse(f'{resource}-detail', args=[record_id])
                self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
                response = self.client.patch(detail, update, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                record = model.objects.get(pk=record_id)
                for field, value in update.items():
                    self.assertEqual(getattr(record, field), value)
                response = self.client.put(detail, {**payload, **update}, format='json')
                self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
                self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)
                self.assertFalse(model.objects.filter(pk=record_id).exists())

    def test_invalid_relationship_is_rejected(self):
        self.client.force_authenticate(self.login_user)
        response = self.client.post(
            reverse('comment-list'),
            {'content': 'Invalid post', 'post': self.post.pk + 1000},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('post', response.data)
