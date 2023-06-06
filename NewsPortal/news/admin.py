"""
В данном файле регистрируются модели, чтобы их можно было видеть в админке
"""
from django.contrib import admin

from .models import Post, Category, Author, Comment, CategorySubscribers


admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Comment)
admin.site.register(CategorySubscribers)

