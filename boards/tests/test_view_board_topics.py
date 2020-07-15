from django.test import TestCase
from django.urls import reverse, resolve

from ..views import TopicListView
from ..models import Board


# Create your tests here.

class BoardTopicsTests(TestCase):
    #  To prepare the environment to run the tests, so to simulate a scenario.
    def setUp(self):
        Board.objects.create(name='Django', description='Django discussion board.')

    # test if Django is returning a status code 200 (success) for an existing Board.
    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    # test if Django is returning a status code 404 (page not found) for a Board
    # that doesn’t exist in the database.
    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 90})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    # test if Django is using the correct view function to render the topics
    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        homepage_url = reverse('home')
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

    # responsible for making sure our view contains the required navigation links.
    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))

