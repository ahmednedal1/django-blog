from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .AI_Content.client import ContentClient
from .AI_Content.services import PostNotFoundError, summarize_post
from .models import Post


class ContentClientTests(SimpleTestCase):
    @patch('blog.AI_Content.client.OpenAI')
    def test_generate_uses_configured_model_and_returns_text(self, sdk):
        sdk.return_value.chat.completions.create.return_value.choices[0].message.content = 'Summary'
        client = ContentClient(api_key='test-key', model='test-model')
        self.assertEqual(client.generate('Summarize this'), 'Summary')
        sdk.assert_called_once_with(api_key='test-key')
        sdk.return_value.chat.completions.create.assert_called_once_with(
            model='test-model', messages=[{'role': 'user', 'content': 'Summarize this'}],
        )


@override_settings(OPENAI_APIKEY='test-key', OPENAI_MODEL='test-model')
class SummarizePostTests(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='Test post', content='Stored database content.')
        self.http = APIClient()
        self.url = reverse('summarize_post', kwargs={'post_id': self.post.pk})

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_service_uses_saved_content_and_returns_trimmed_summary(self, client):
        client.return_value.generate.return_value = '  A short summary.  '
        before = Post.objects.count()
        result = summarize_post(self.post.pk)
        self.assertEqual(result, {
            'post_id': self.post.pk,
            'title': 'Test post',
            'summary': 'A short summary.',
            'length': len('A short summary.'),
        })
        client.assert_called_once_with(api_key='test-key', model='test-model')
        client.return_value.generate.assert_called_once()
        self.assertIn(self.post.content, client.return_value.generate.call_args.args[0])
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'Stored database content.')
        self.assertEqual(Post.objects.count(), before)

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_summary_limit_and_empty_response(self, client):
        client.return_value.generate.return_value = '  ' + 'x' * 501 + '  '
        result = summarize_post(self.post.pk)
        self.assertEqual(result['summary'], 'x' * 500)
        self.assertEqual(result['length'], 500)
        client.return_value.generate.assert_called_once()
        for empty in ('', '  \n  ', None):
            with self.subTest(empty=empty):
                client.return_value.generate.return_value = empty
                with self.assertRaisesMessage(ValueError, 'summary is empty'):
                    summarize_post(self.post.pk)

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_invalid_ids_missing_posts_and_empty_content_do_not_call_client(self, client):
        for invalid in (0, -1, '1', None, True, 1.2):
            with self.subTest(invalid=invalid):
                with self.assertRaisesMessage(ValueError, 'positive integer'):
                    summarize_post(invalid)
        with self.assertRaises(PostNotFoundError) as caught:
            summarize_post(self.post.pk + 1000)
        self.assertIsInstance(caught.exception, ValueError)
        for empty in ('', '   \n '):
            self.post.content = empty
            self.post.save()
            with self.assertRaisesMessage(ValueError, 'Post content'):
                summarize_post(self.post.pk)
        client.assert_not_called()

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_endpoint_uses_database_content_not_request_body(self, client):
        client.return_value.generate.return_value = 'A summary'
        response = self.http.post(self.url, {'content': 'Ignore this request content'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'post_id': self.post.pk, 'title': self.post.title,
            'summary': 'A summary', 'length': 9,
        })
        prompt = client.return_value.generate.call_args.args[0]
        self.assertIn('Stored database content.', prompt)
        self.assertNotIn('Ignore this request content', prompt)
        client.return_value.generate.assert_called_once()

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_endpoint_returns_json_errors_and_rejects_get(self, client):
        missing = self.http.post(f'/blog/posts/{self.post.pk + 1000}/summarize/')
        self.assertEqual(missing.status_code, 404)
        self.assertIn('not found', missing.json()['error'])
        invalid = self.http.post('/blog/posts/0/summarize/')
        self.assertEqual(invalid.status_code, 400)
        self.assertIn('positive integer', invalid.json()['error'])
        self.post.content = '   '
        self.post.save()
        empty = self.http.post(self.url)
        self.assertEqual(empty.status_code, 400)
        self.assertIn('Post content', empty.json()['error'])
        self.assertEqual(self.http.get(self.url).status_code, 405)
        client.assert_not_called()

    @patch('blog.AI_Content.services.summarize.ContentClient')
    def test_endpoint_rejects_blank_generated_summary(self, client):
        client.return_value.generate.return_value = '  '
        response = self.http.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('summary is empty', response.json()['error'])
