from django.contrib import admin
from django.urls import path, include

# for logout
from django.contrib.auth import views as auth_views

# for signup
from accounts import views as accounts_views

from boards import views as board_views


urlpatterns = [
    path('admin/', admin.site.urls),


    path('boards/signup/', accounts_views.signup, name='signup'),

    path('boards/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Inside the as_view() we can pass some extra parameters, so to override
    # the defaults. In this case, we are instructing the LoginView
    # to look for a template at login.html.
    path('boards/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),



    # change password urls: works for only logged in users
    path('boards/settings/password', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('boards/settings/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),



    # reset password urls
    path('boards/reset/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt'
    ), name='password_reset'),

    path('boards/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_done'),

    path('boards/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'
    ), name='password_reset_confirm'),

    path('boards/accounts/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'
    ), name='password_reset_complete'),



    path('boards/', board_views.BoardListView.as_view(), name='home'),
    path('boards/<int:pk>/', board_views.TopicListView.as_view(), name='board_topics'),
    path('boards/<int:pk>/new', board_views.new_topic, name='new_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>', board_views.PostListView.as_view(), name='topic_posts'),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply', board_views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/', board_views.PostUpdateView.as_view(), name='edit_post'),
    path('boards/settings/account', board_views.UserUpdateView.as_view(), name='my_account'),

]
