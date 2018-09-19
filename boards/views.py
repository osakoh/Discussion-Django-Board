from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, ListView
from django.utils import timezone

# the person must  be logged in to see the view- new_topic
from django.contrib.auth.decorators import login_required

# login decorator for CBV
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User


# Create your views here.
class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


# pk is the keyword argument
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 16

    # how to add stuff to the request context when extending a GCBV.
    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


# new_topic we are using topic.pk because a topic is an
# object (Topic model instance) and .pk we are accessing the pk property of the
# Topic model instance.
# - set the proper user, instead of just querying the database and
# picking the first user.
# redirects to the login page if the person isn't logged in
@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    #  If the request came from a POST, it means the user is submitting some data.
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            # redirects to the created topic page
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)

    else:
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 15

    # session_key:To prevent the same user from refreshing the page thereby making
    # the page count as multiple views
    def get_context_data(self, *, object_list=None, **kwargs):
        session_key = 'viewed_topic{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email',)
    template_name = 'my_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user


# reply_topic we are using topic_pk because we are referring
# to the keyword argument of the function
@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    # used to identify the name of the keyword argument used to retrieve the Post object
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    # With the line queryset = super().get_queryset() we are reusing the get_queryset
    # method from the parent class, that is, the UpateView class. Then, we are adding
    # an extra filter to the queryset, which is filtering the post using the logged in
    #  user, available inside the request object.    '''
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


"""
*************************************************************************************************
# pk is the keyword argument
# def board_topics(request, pk):
#     board = get_object_or_404(Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
# 
#     paginator = Paginator(queryset, 16)
# 
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         # goes back to the first page
#         topics = paginator.page(1)
#     except EmptyPage:
#         # probably the user tried to add a page number
#         # in the url, so we fallback to the last page
#         topics = paginator.page(paginator.num_pages)
# 
#     return render(request, 'topics.html', {'board': board, 'topics': topics})

****************************************************************************************************

# def home(request):
#     boards = Board.objects.all()
#     return render(request, 'home.html', {'boards': boards})

******************************************************************************************************

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

******************************************************************************************************
"""

