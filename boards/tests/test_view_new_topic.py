from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from ..views import new_topic
from ..models import Board, Topic, Post
from ..forms import NewTopicForm


# Create your tests here.

class NewTopicTests(TestCase):
    #  creates a Board instance to be used during the tests
    # included the User.objects.create_user to create
    # a User instance to be used in the tests
    def setUp(self):
        Board.objects.create(name='Django', description='Django test board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')  # <- included this line here
        self.client.login(username='john', password='123')

    # check if the request to the view is successful
    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    # check if the view is raising a 404 error when the Board does not exist
    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    # check if the right view is being used
    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new')
        self.assertEquals(view.func, new_topic)

    # ensure the navigation back to the list of topics
    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    # since the CSRF Token is a fundamental part of processing POST requests,
    # we have to make sure our HTML contains the token.
    def test_csrf(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    # sends a valid combination of data and check if the view created a
    # Topic instance and a Post instance.
    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    # Invalid post data should not redirect
    # The expected behavior is to show the form again with validation errors
    def test_new_topic_invalid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    # Invalid post data should not redirect
    # The expected behavior is to show the form again with validation errors
    # here we are sending an empty dictionary to check how the application is behaving.
    def test_new_topic_invalid_post_data_empty_fields(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {'subject': '', 'message': ''}
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    # make a request to the new topic view without being authenticated.
    # The expected result is for the request be redirected to the login view.
    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
