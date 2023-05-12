from django.shortcuts import render, redirect
from .models import Post, Review, Comment, ReviewReport
from .forms import PostForm, ReviewForm, CommentForm, ReviewReportForm
import os, json
import requests
import pprint
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Create your views here.

TMDB_API_KEY = 'dfc02edc73a8a31017aeb0d746f5753d'

def index(request):
# 플랫폼별 TOP10
# 최신 상영작 
# 많이 본 순 - 완 
# 별점 높은 순 - 완
# 장르별 추천영화 - 완 
# 태그별 추천영화 
# 검색

    # 최신 상영작을 평점 순으로 나열하여 5개만 불러옵니다.
    now_playing_url = 'https://api.themoviedb.org/3/movie/now_playing'

    params = {
        'api_key': TMDB_API_KEY,
        'language': 'ko-kr',
        'region':'kr',
        'page': 1,
    }
    now_playing_response = requests.get(now_playing_url, params=params)
    now_playing_data = now_playing_response.json()
    now_playing = sorted(now_playing_data['results'], key=lambda x:x['vote_average'], reverse=True)[:10]


    # popular 순위 (1페이지~ 10페이지, 페이지당 20개, 총 200개)
    total_data = []   

    for i in range(1, 10):
        popular_url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=ko-KR&page={i}"
        popular = requests.get(popular_url).json()

        for movie in popular['results']:
            if movie.get("release_date") is not None:
                fields = {
                    'movie_id': movie['id'],
                    'title': movie['title'],
                    'released_date': movie['release_date'],
                    'rating': movie['vote_average'],
                    'description': movie['overview'],
                    'poster_path': movie['poster_path'],
                    'category': movie['genre_ids'],
                    # 'nation': movie['production_countries'],
                    # 'runnigtime': movie['runtime'],

                }

                # movie['tags'] = ['#손에 땀을 쥐게 하는', '#결말이 아름다운']

                data = {
                    "pk": movie['id'],
                    "model": "movies.movie",
                    "fields": fields
                }

                total_data.append(data)

    # json 파일 생성
    with open("movie_data.json", "w", encoding="utf-8") as w:
        json.dump(total_data, w, indent="\\t", ensure_ascii=False)


    # # 최신순 
    # latest_movie_list = list()
    # for i in range(1, 10):
    #     latest_url = 'https://api.themoviedb.org/3/movie/latest'
    #     params = {
    #         'api_key': TMDB_API_KEY,
    #         'language': 'ko-kr',
    #         'region':'kr',
    #         'page': i, 
    #     }

    #     latest_response = requests.get(latest_url, params=params)
    #     latest_data = latest_response.json()
    #     print("--------------------------------")
    #     pprint.pprint(latest_data)
    #     # latest = sorted(latest_data, key=lambda x:x['vote_average'], reverse=True)
    #     latest_movie_list.append(latest_data)
    #     # print("--------------------------------")
    #     # pprint.pprint(latest_movie_list)
        

    #장르번호 딕셔너리
    genre_dict = {
        28: '액션',
        12: '모험',
        16: '애니메이션',
        35: '코미디',
        80: '범죄',
        99: '다큐멘터리',
        18: '드라마',
        10751: '가족',
        14: '판타지',
        36: '역사',
        27: '공포',
        10402: '음악',
        9648: '미스터리',
        10749: '로맨스',
        878: 'SF',
        10770: 'TV 영화',
        53: '스릴러',
        10752: '전쟁',
        37: '서부'
    }

    # 장르별 영화 5개씩
    genre_movie_list = list()
    for page in range(1, 5):
        genre_url = 'https://api.themoviedb.org/3/movie/top_rated'

        params = {
            'api_key': TMDB_API_KEY,
            'language': 'ko-kr',
            'region':'kr',
            'page': page
        }

        genre_response = requests.get(genre_url, params=params)
        genre_data = genre_response.json()
        genre = sorted(genre_data['results'], key=lambda x:x['vote_average'], reverse=True)
        genre_movie_list.append(genre)

    # 평점순
    top_rated_movie_list = list()
    for page in range(1, 5):
        top_rated_url = 'https://api.themoviedb.org/3/movie/top_rated'

        params = {
            'api_key': TMDB_API_KEY,
            'language': 'ko-kr',
            'region':'kr',
            'page': page,
        }
        
        
        top_rated_response = requests.get(top_rated_url, params=params)
        top_rated_data = top_rated_response.json()
        top_rated = sorted(top_rated_data['results'], key=lambda x:x['vote_average'], reverse=True)
        top_rated_movie_list.append(top_rated)
    


    context={
        'now_playing': now_playing,
        'total': total_data,
        'popular' : popular,
        'genre_dict' : genre_dict, 
        'genre': genre,
        'top_rated': top_rated,
        'genre_movie_list' : genre_movie_list
       
    }
    return render(request, 'movies/index.html', context)



def detail(request, movie_id):
    try:
        post = Post.objects.get(movie_id=movie_id)
    except Post.DoesNotExist:
        post = None    
    detail_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    similar_url = f'https://api.themoviedb.org/3/movie/{movie_id}/similar'
    
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'ko-kr',
        'region':'kr',
    
    }
    detail_response = requests.get(detail_url, params=params)
    detail_data = detail_response.json()

    similar_response = requests.get(similar_url, params=params)
    similar_data = similar_response.json()
    similars = sorted(similar_data['results'], key=lambda x:x['vote_average'], reverse=True)
   
    
    context = {
        'detail_data':detail_data,
       # 'keyword_data': keyword_data,
        'movie_id' : movie_id,
        'similars' : similars,
       
        
    }
    return render(request, 'movies/detail.html', context)

def search(request):
    query = request.GET.get('query')
    search_url = 'https://api.themoviedb.org/3/search/movie'
    person_url = 'https://api.themoviedb.org/3/search/person'

    # search_url = 'https://api.themoviedb.org/3/search/multi'

    params = {
        'api_key': TMDB_API_KEY,
        'language': 'ko-kr',
        'region':'kr',
        'query': query,
    
    }
    
    search_response = requests.get(search_url, params=params)
    search_data = search_response.json()
    pprint.pprint(search_data)
    
    person_response = requests.get(person_url, params=params)
    person_search_data = person_response.json()
    
    
    movie_image = 'https://image.tmdb.org/t/p/w200' 
    for movie in search_data['results']:
        if movie['poster_path']: 
            movie['poster_path'] = movie_image + movie['poster_path']
            
    person_image = 'https://image.tmdb.org/t/p/w200'
    for person in person_search_data['results']:
        if person.get('profile_path'):
            person['profile_path'] = person_image + person['profile_path']
            
    # 검색한 배우의 출연 영화 목록
    movies_cast = []
    movie_posters = []
    movies = []

    if 'results' in person_search_data and person_search_data['results']:
        for person in person_search_data['results']:
            if person.get('profile_path'):
                person_id = person['id']
                credit_url = f"https://api.themoviedb.org/3/person/{person_id}/movie_credits"
                credit_params = {
                    'api_key': TMDB_API_KEY,
                    'language': 'ko-kr',
                }
                credit_response = requests.get(credit_url, params=credit_params)
                credit_data = credit_response.json()

                movies = []
                if 'cast' in credit_data:
                    sorted_actor_movies = sorted(credit_data['cast'], key=lambda x: x['release_date'], reverse=True)

                    for actor_movie in sorted_actor_movies:
                        if len(movies) >= 4:
                            break

                        if actor_movie.get('poster_path'):
                            actor_movie_image = 'https://image.tmdb.org/t/p/w200'
                            actor_movie['poster_path'] = actor_movie_image + actor_movie['poster_path']
                            movie_posters.append(actor_movie)
                            movies.append(actor_movie['title'])

                    if movies:
                        person_name = person['name']
                        is_check = False
                        for cast in movies_cast:
                            if cast['person_name'] == person_name:
                                is_check = True
                                break

                        if not is_check:
                            movies_cast.append({
                                'person_name': person_name,
                                'movies': movies,
                            })
    
    sorted_data = sorted(search_data['results'], key=lambda x: x['release_date'], reverse=True)
    
    page = request.GET.get('page', '1')
    per_page = 12
    paginator = Paginator(sorted_data, per_page)
    posts = paginator.get_page(page)
    
    # 사이트가 안들어가져서 잠시만 주석처리할게요..ㅠ 네 !!
    # if query in request.GET:
        
    
    genre_dict = {
        28: '액션',
        12: '모험',
        16: '애니메이션',
        35: '코미디',
        80: '범죄',
        99: '다큐멘터리',
        18: '드라마',
        10751: '가족',
        14: '판타지',
        36: '역사',
        27: '공포',
        10402: '음악',
        9648: '미스터리',
        10749: '로맨스',
        878: 'SF',
        10770: 'TV 영화',
        53: '스릴러',
        10752: '전쟁',
        37: '서부'
    }
    
    context = {
        'search_data' : search_data,
        'person_search_data': person_search_data,
        'movies' : movies,
        'posts': posts,
        'query' : query,
        'movies_cast': movies_cast,
        'movie_posters': movie_posters,
        'genre_dict': genre_dict,
    }
    
    return render(request, 'movies/search.html', context)

@login_required
def create(request, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=ko-KR'
    response = requests.get(url)
    movie_data = response.json()
    poster_path = 'https://image.tmdb.org/t/p/w200' + movie_data.get('poster_path')
    # if request.user != 'admin':
    #     return redirect('movies:index')
    if Post.objects.filter(movie_id=movie_id).exists():
        return redirect('movies:index')
    
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = PostForm(request.POST)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.movie_id = movie_id
                    post.user = request.user
                    post.poster_path = poster_path
                    post.title = movie_data.get('title')
                    post.movie_overview = movie_data.get('overview')
                    post.movie_release_date = movie_data.get('release_date')
                    post.ratings = movie_data.get('score')
                    post.tags = form.cleaned_data.get('tags', [])  
                    post.platform = form.cleaned_data.get('platform', [])  


                    # ratings = float(request.POST['ratings'])
                    # post.ratings = ratings
                    post.save()
                    return redirect('movies:detail', movie_id)
            
            #템플릿에서 다중 선택된 값들을 렌더링하기 위해 폼을 다시 표시할 때, 이전에 선택된 값들이 표시되도록 폼을 초기화할 수 있습니다. 
            else:
                form = PostForm(initial={'tags': Post.objects.values_list('tags', flat=True)}) 
            context = {
                'form': form,
                'movie': movie_data,
            }
            return render(request, 'movies/create.html', context)
        else:
            return redirect('movies:index')

def similar(request, movie_id):
    similar_url = f'https://api.themoviedb.org/3/movie/{movie_id}/similar'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'ko-kr',
        'region':'kr',
    
    }
    similar_response = requests.get(similar_url, params=params)
    similar_data = similar_response.json()
    similars = sorted(similar_data['results'], key=lambda x:x['vote_average'], reverse=True)
    # print(similar_data)
    context = {
        'similar_data':similar_data,
        'similars' : similars,
        
        
    }
    return render(request, 'movies/detail.html', context)

def get_movie_info(movie_id):
    get_movie_url = f'https://api.themoviedb.org/3/movie/{movie_id}'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'ko-kr',
        'region':'kr',
    }
    get_movie_response = requests.get(get_movie_url, params=params)
    # movie_data = get_movie_response.json()
    # return movie_data
    if get_movie_response.status_code == 200:
        movie_data = get_movie_response.json()
        return movie_data
    return None
    
@login_required
def review_create(request, movie_id):
    movie = get_movie_info(movie_id)
    
    post = Post.objects.get(movie_id=movie_id)
    # post = Post.objects.get(pk=post_pk)
    print(post)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.post = post        
            review.user = request.user
            review.tags = form.cleaned_data.get('tags', [])
            review.save()
            return redirect('movies:detail', post.movie_id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'post': post,
    }
    
    return render(request, 'movies/review_create.html', context)

@login_required
def review_delete(request, movie_id, review_id):
    review = Review.objects.get(id=review_id)
    if request.user == review.user:
        review.delete()
    
    return redirect('movies:detail', movie_id)

@login_required
def review_update(request, movie_id, review_id):
    post = Post.objects.get(movie_id=movie_id)

    # post = Post.objects.get(pk=post_pk)
    # movie_id = post.movie_id
    review = Review.objects.get(id=review_id)

    # try:
    #     review = Review.objects.get(id=review_id)
    # except Review.DoesNotExist:
    #     return redirect('movies:detail', movie_id )

    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('movies:detail', post.movie_id)
        else:
            form = ReviewForm(instance=review)
    else:
        return redirect('movies:detail', post.movie_id)
    
    context = {
        'review': review,
        'form': form,
        'post': post,
    }
    
    return render(request, 'movies/review_update.html', context)

@login_required
def wants(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user in post.want_users.all():
        post.want_users.remove(request.user)
        is_wanted = False
    else:
        post.want_users.add(request.user)
        is_wanted = True
    context = {
        'is_wanted': is_wanted,
    }
    return JsonResponse(context)

@login_required
def watchings(request, post_pk):
    post = Post.objects.get(pk=post_pk)
    if request.user in post.watching_users.all():
        post.watching_users.remove(request.user)
        watching = False
    else:
        post.watching_users.add(request.user)
        watching = True
    context = {
        'watching': watching,
    }
    return JsonResponse(context)



@login_required
def review_detail(request, movie_id, review_id):
    post = Post.objects.get(movie_id=movie_id)
    review = Review.objects.get(id=review_id)
    # movie_title = post.movie.title
    context = {
      'post':post,
      'review':review,
    #   'movie_title':movie_title,
    }
    return render(request, 'movies/review_detail.html', context)


@login_required
def review_like(request, movie_id, review_id):
  review = Review.objects.get(id=review_id)

  if request.user in review.like_users.all():
      review.like_users.remove(request.user)
      is_liked = False
  else:
      review.like_users.add(request.user)
      is_liked = True
  context = {
    'is_liked':is_liked,
  }
  return JsonResponse(context)

@login_required
def comment_create(request, movie_id, review_id):
    review = Review.objects.get(id=review_id)
    # movie = Post.objects.get(movie_id=movie_id)
    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
            return redirect('movies:review_detail',movie_id, review_id)
    else:
        form = CommentForm()
    context = {
    'form':form,
    'review':review,
    }
    return render(request, 'movies/comment_create.html', context)

@login_required
def review_report(request, movie_id, review_id):
    review = Review.objects.get(id=review_id)
    form = ReviewReportForm()

    if request.method == 'POST':
        form = ReviewReportForm(request.POST)
        if form.is_valid():
            review_report = form.save(commit=False)
            review_report.review = review
            review_report.user = request.user
            review_report.save()
            return redirect('movies:detail', movie_id)
            
    context = {
        'review': review,
        'form': form,
        'movie_id' : movie_id,
        'review_id' : review_id,
    }
    return render(request, 'movies/review_report.html', context)