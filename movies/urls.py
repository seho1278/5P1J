from django.urls import path

from . import views


app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('<int:movie_id>/similar/', views.similar, name='similar'),
    path('create/<int:movie_id>/', views.create, name='create'),
    path('<int:movie_id>/reviews/', views.review_create, name='review_create'),
    path('<int:movie_id>/reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('<int:movie_id>/reviews/<int:review_id>/update/', views.review_update, name='review_update'),
    path('<int:post_pk>/wants/', views.wants, name='wants'),
    path('<int:post_pk>/watchings/', views.watchings, name='watchings'),

    # path('<int:movie_id>/reviews/<int:review_id>/update/', views.review_update, name='review_update'),
    # path('<int:movie_pk>/reviews/<int:review_pk>/delete/', views.review_delete, name='review_delete'),

    # path('<int:movie_id>/reviews/<int:review_id>/comment/create', views.comment_create, name='comment_create'),
]