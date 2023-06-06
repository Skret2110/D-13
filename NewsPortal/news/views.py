"""
В данном файле прописывается логика приложения.
Суть представления(views) в джанго - это запрос ин-ии из модели в файле models и
передача ее в шаблон(templates)

После создания представлений, нужно указать адреса, по которым будут доступны представления.
Для настройки адресов используется файл "urls.py" но не тот, который лежит в проекте, а тот
что нужно создать в приложении и указать на него ссылкой из основного файла.

Django поддерживает несколько разных видов представлений:
1) Class-based views — представления, организованные в виде классов.
2) Generic class-based views — часто используемые представления, которые Django предлагает в виде решения «из коробки».
   Они реализуют в первую очередь функционал CRUD (Create Read Update Delete).
3) Function-based views — представления в виде функций.

"""
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.core.cache import cache
from .filters import PostFilter
from .forms import PostForm
from .models import Post, Category
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from .tasks import hello, printer
import logging

logger = logging.getLogger(__name__)


class PostList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    ordering = ['-id']
    paginate_by = 1


class PostsSearch(ListView):
    model = Post
    template_name = 'news/search.html'
    context_object_name = 'posts_search'
    ordering = ['-time_of_creation']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostDetailView(DetailView):
    template_name = 'news/post_detail.html'
    queryset = Post.objects.all()

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)

        return obj


class PostCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'news/post_add.html'
    form_class = PostForm
    permission_required = ('news.add_post',)

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        post_category_pk = request.POST['post_category']
        sub_text = request.POST.get('text')
        sub_title = request.POST.get('title')
        post_category = Category.objects.get(pk=post_category_pk)
        subscribers = post_category.subscribers.all()
        host = request.META.get('HTTP_HOST')

        if form.is_valid():
            news = form.save(commit=False)
            news.save()

        for subscriber in subscribers:
            html_content = render_to_string(
                'news/mail.html', {'user': subscriber, 'text': sub_text[:50], 'post': news, 'title': sub_title, 'host': host}
            )

            msg = EmailMultiAlternatives(
                subject=f'Здравствуй, {subscriber.username}. Новая статья в вашем разделе!',
                body=f'{sub_text[:50]}',
                from_email='fedorenko.i.2110@yandex.ru',
                to=[subscriber.email],
            )

            msg.attach_alternative(html_content, "text/html")
            msg.send()
        return redirect('/posts/')


class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'news/post_add.html'
    form_class = PostForm
    permission_required = ('news.change_post',)

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = 'news/post_delete.html'
    permission_required = ('news.delete_post',)
    queryset = Post.objects.all()
    success_url = '/posts/'


class CategoryList(ListView):
    model = Category
    template_name = 'news/category_list.html'
    context_object_name = 'categories'


class CategoryDetail(DetailView):
    template_name = 'news/category_subscription.html'
    model = Category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('pk')
        category_subscribers = Category.objects.filter(pk=category_id).values("subscribers__username")
        context['is_not_subscribe'] = not category_subscribers.filter(subscribers__username=self.request.user).exists()
        context['is_subscribe'] = category_subscribers.filter(subscribers__username=self.request.user).exists()
        return context


@login_required
def add_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'добавлен в подписчики категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.add(request.user)
    return redirect('/posts/categories')


@login_required
def del_subscribe(request, **kwargs):
    pk = request.GET.get('pk', )
    print('Пользователь', request.user, 'удален из подписчиков категории:', Category.objects.get(pk=pk))
    Category.objects.get(pk=pk).subscribers.remove(request.user)
    return redirect('/posts/categories')


class IndexView(View):
    def get(self, request):
        printer.apply_async([10],
                            eta=datetime.now() + timedelta(seconds=5))
        hello.delay()
        return HttpResponse('Hello!')



