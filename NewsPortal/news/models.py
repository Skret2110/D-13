"""
В данном файле создаются и описываются сущности баз данных(БД).
Описываются их поля(атрибуты) и методы.
Для этого используются приемы ООП, а именно - Классы.
Также здесь описываются все связи между сущностями:
один ко многим (One to Many)
многие ко многим (Many to Many)
один к одному (One to one)
Когда модели созданы, их нужно передать в файл "views.py"
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.core.cache import cache


class Author(models.Model):
    author_user = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    def update_rating(self):
        author_post_rating = self.post_set.aggregate(postRating=Sum('post_rating'))
        p_rat = 0
        p_rat += author_post_rating.get('postRating')

        author_comment_rating = self.author_user.comment_set.aggregate(commentRating=Sum('comment_rating'))
        c_rat = 0
        c_rat += author_comment_rating.get('commentRating')

        self.author_rating = p_rat * 3 + c_rat
        self.save()

    def __str__(self):

        return f'{self.author_user}'


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    subscribers = models.ManyToManyField(User, through='CategorySubscribers')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return f'{self.name}'


class CategorySubscribers(models.Model):
    sub_categories = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.sub_categories}, {self.sub_users}'


class Post(models.Model):
    article = 'AR'
    news = 'NW'

    kind = [
        (article, 'Статья'),
        (news, 'Новость')
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    view = models.CharField(max_length=2, choices=kind, default=article)
    time_of_creation = models.DateTimeField(auto_now_add=True)
    post_category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория(category)')
    title = models.CharField(max_length=128)
    text = models.TextField()
    post_rating = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return f'{self.title.title()}: {self.get_view_display()}'

    def like(self,):
        self.post_rating += 1
        self.save()

    def dislike(self,):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return f'{self.text[:125]} + {"..."}'

    # def get_absolute_url(self):
    #     return f'/posts/{self.id}'

    def get_absolute_url(self):
        return f'/posts/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self,):
        self.comment_rating -= 1
        self.save()
