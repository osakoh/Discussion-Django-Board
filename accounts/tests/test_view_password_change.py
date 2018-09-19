from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User


#  It does a basic setup, creating a user and making a POST
# request to the password_change view
class PasswordChangeTestCase(TestCase):
    def setUp(self, data={}):
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data)


# The test above tries to access the password_change view without
#  being logged in. The expected behavior is to redirect the user
# to the login page
class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

    def test_redirection(self):
        # A valid form submission should redirect the user
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self):
        # refresh the user instance from database to get the new password
        # hash updated by the change password view.
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        # Create a new request to an arbitrary page.
        # The resulting response should now have an `user` to its context, after a successful sign up.
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def test_status_code(self):
        # An invalid form submission should return to the same page
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        # refresh the user instance from the database to make
        # sure we have the latest data because the
        # change_password view update the password
        # in the database. So to test if the password really
        # changed, we have to grab the latest data from the
        # database.
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))