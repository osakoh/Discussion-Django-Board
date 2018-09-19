from django import forms
from .models import Topic, Post


# A ModelForm associated with the Topic model.
class NewTopicForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(
        attrs={'rows': 5, 'placeholder': 'Share your thoughts?'}
    ),
                              max_length=4000,
                              help_text='The max length of the text shouldn\'t exceed 4000.'
                              )

    # The subject in the fields list inside the Meta class is referring to the
    # subject field in the Topic class.
    class Meta:
        model = Topic
        fields = ['subject', 'message']


# to reply a post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]