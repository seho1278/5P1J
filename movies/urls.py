from django.urls import path

from . import views


app_name = 'movies'
urlpatterns = [
    path('', views.index, name='index'),
    # 추가
    path('main/', views.main, name='main'),
    path('<int:movie_id>/', views.detail, name='detail'),
    path('<int:movie_id>/similar/', views.similar, name='similar'),
    path('create/<int:movie_id>/', views.create, name='create'),
    path('<int:movie_id>/delete/', views.delete, name='delete'),
    path('<int:movie_id>/reviews/', views.review_create, name='review_create'),
    path('<int:movie_id>/reviews/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('<int:movie_id>/reviews/<int:review_id>/update/', views.review_update, name='review_update'),
    path('<int:movie_id>/reviews/<int:review_id>/review_report/', views.review_report, name='review_report'),
    path('<int:post_pk>/wants/', views.wants, name='wants'),
    path('<int:post_pk>/watchings/', views.watchings, name='watchings'),
    path('search/', views.search, name='search'),
    path('<int:movie_id>/reviews/<int:review_id>/detail/', views.review_detail, name='review_detail'),
    path('<int:movie_id>/reviews/<int:review_id>/comment/create/', views.comment_create, name='comment_create'),
    path('<int:movie_id>/reviews/<int:review_id>/comment/<int:comment_id>/update/', views.comment_update, name='comment_update'),
    path('<int:movie_id>/reviews/<int:review_id>/comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:movie_id>/reviews/<int:review_id>/like/', views.review_like, name='review_like'),
    path('<int:movie_id>/reviews/<int:review_id>/comment/<int:comment_id>/like/', views.comment_like, name='comment_like'),

]