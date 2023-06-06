"""
Данный файл отвечает за реализацию представлений приложения "sign",
которое используется для регистрации и входа пользователей
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from news.models import Author
from .models import BaseRegisterForm


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/posts/profile'


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(author_user=user)
    return redirect('/account/profile/')


@login_required
def not_author(request):
    user = request.user
    user_id = request.user.pk
    print(user_id)
    author_delete = Author.objects.get(author_user=user)
    authors_group = Group.objects.get(name='authors')
    if request.user.groups.filter(name='authors').exists():
        authors_group.user_set.remove(user)
        author_delete.delete()
    return redirect('/account/profile/')
