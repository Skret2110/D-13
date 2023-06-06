"""
Данный файл описывает продолжение адреса для конкретного приложения.
То есть главный файл urls.py ссылается на файл news.urls и приписывает в начале адреса: posts/ (например)
после чего начинают действовать адреса, указанные в этом файле в переменной "urlpatterns"
Главный файл забирает все адреса из этого файла, чтобы выстроить полный путь
"""

from django.urls import path, include
# from django.views.decorators.cache import cache_page

from .views import PostList, PostsSearch, PostDetailView, \
    PostCreateView, PostUpdateView, PostDeleteView, \
    CategoryList, add_subscribe, del_subscribe, CategoryDetail

urlpatterns = [
    path('', PostList.as_view(), name='posts'),
    path('search/', PostsSearch.as_view(), name='search'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('add/', PostCreateView.as_view(), name='post_add'),
    path('add/<int:pk>', PostUpdateView.as_view(), name='post_update'),
    path("account/", include("allauth.urls")),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='post_delete'),
    path('categories/', CategoryList.as_view(), name='categories'),
    path('categories/<int:pk>/add_subscribe/', add_subscribe, name='add_subscribe'),
    path('categories/<int:pk>/del_subscribe/', del_subscribe, name='del_subscribe'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category_subscription'),


]
