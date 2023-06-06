import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from datetime import datetime

from news.models import Category, Post


logger = logging.getLogger(__name__)


def news_sender():
    for category in Category.objects.all():
        news_from_each_category = []
        week_number_last = datetime.now().isocalendar()[1]-1
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


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.add_job(
            news_sender,
            trigger=CronTrigger(day_of_week="mon", hour="08", minute="00"),
            id="news_sender",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена работка 'news_sender'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Задачник запущен")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Задачник остановлен")
            scheduler.shutdown()
            logger.info("Задачник остановлен успешно!")
