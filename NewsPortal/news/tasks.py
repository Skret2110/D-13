"""
Этот файл нужен для создания задач (D7).
"""
import logging
import time
from datetime import date, datetime

from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string

from NewsPortal.settings import SITE_URL, DEFAULT_FROM_EMAIL
from news.models import Post, Category
logger = logging.getLogger(__name__)

@shared_task
def new_post_notify(intance_id):
    intance = Post.objects.get(pk=intance_id)
    categories = intance.post_category.all()
    subscribers = []

    for category in categories:
        subscribers += category.subscribers.all()

    for mail in subscribers:
        html_content = render_to_string(
            'new_post_created.html',
            {'text': intance.preview, 'link': f'{SITE_URL}/posts/{intance_id}'}
        )

        msg = EmailMultiAlternatives(
            subject=intance.title,
            body='',
            from_email=DEFAULT_FROM_EMAIL,
            to=[mail]
        )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()

@shared_task
def hello():
    time.sleep(10)
    print('Hello, world!')


@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)



@shared_task
def news_sender():
    for category in Category.objects.all():
        news_from_each_category = []
        week_number_last = datetime.utcnow().isocalendar()[1]-1
        for post in Post.objects.filter(post_category_id=category.id,
                                        time_of_creation__week=week_number_last).values('pk',
                                                                                        'title',
                                                                                        'time_of_creation',
                                                                                        'post_category_id__name'):

            date_format = post.get("time_of_creation").strftime("%d/%m/%Y")
            post = (f' http://127.0.0.1:8000/posts/{post.get("pk")}, Заголовок: {post.get("title")}, '
                   f'Категория: {post.get("post_category_id__name")}, Дата создания: {date_format}')
            news_from_each_category.append(post)

        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            html_content = render_to_string(
                'news/mail_sender.html', {'user': subscriber,
                                          'text': news_from_each_category,
                                          'category_name': category.name,
                                          'week_number_last': week_number_last})

            msg = EmailMultiAlternatives(
                subject=f'Здравствуй, {subscriber.username}, новые статьи за прошлую неделю в вашем разделе!',
                from_email='fedorenko.i.2110@yandex.ru',
                to=[subscriber.email]
            )

            msg.attach_alternative(html_content, 'text/html')
            msg.send()
