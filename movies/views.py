from django.shortcuts import render, redirect
from .models import Post, Review, Comment
from .forms import PostForm, ReviewForm
import os, json
import requests
import pprint
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
        'movie_id' : movie_id,
        'similars' : similars,
       
        
    }
    return render(request, 'movies/detail.html', context)

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
    

def review_create(request, movie_id):
    movie = get_movie_info(movie_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.post = movie
            review.user = request.user
            review.save()
            return redirect('movies:detail', movie_id=movie_id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'movie': movie,
    }
    
    return render(request, 'movies/review_create.html', context)


def review_delete(request, movie_id, review_id):
    # post = Post.objects.get(id=movie_id)
    review = Review.objects.get(id=review_id)
    if request.method == "POST":
        review.delete()
    
    return redirect('movies:detail', movie_id)

# def comment_create(request, movie_id, review_id):