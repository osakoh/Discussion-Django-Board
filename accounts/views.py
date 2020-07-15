from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login


from .forms import SignUpForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            # If the form is valid, a User instance is created with the
            # user = form.save().

            user = form.save()
            # The created user is then passed as an argument to the
            # auth_login function, manually authenticating the user.
            auth_login(request, user)
            # the view redirects the user to the homepage
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})