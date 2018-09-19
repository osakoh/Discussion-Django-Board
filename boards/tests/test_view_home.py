from django.test import TestCase
from django.urls import reverse, resolve

from ..views import BoardListView
from ..models import Board


# Create your tests here.
class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django test board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        # testing the status code of the response. The status code 200 means success.
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolvers_home_view(self):
        # makes sure the URL (boards/) which is the root URL, is returning the home view
        view = resolve('/boards/')

        # for Function Views : self.assertEquals(view.func, BoardListView)
        self.assertEquals(view.func.view_class, BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        # Here we are using the assertContains method to test if the response body
        # contains a given text. The text we are using in the test, is the href part
        #  of an a tag. So basically we are testing if the response body has the text href="/boards/1/".
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))

