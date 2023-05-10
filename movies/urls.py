from django.urls import path, include

from . import views


app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    # path('<int:movie_pk>/reviews/', views.review_create, name='review_create'),
    # path('<int:movie_pk>/reviews/<int:review_pk>/delete/', views.review_delete, name='review_delete'),
]