from django.shortcuts import render
import os, json
import requests
import pprint
# Create your views here.

TMDB_API_KEY = 'dfc02edc73a8a31017aeb0d746f5753d'

def index(request):
# 플랫폼별 TOP10
# 최신 상영작 - 완
# 많이 본 순 - 완 
# 별점 높은 순 
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
    now_playing = sorted(now_playing_data['results'], key=lambda x:x['vote_average'], reverse=True)[:5]

    total_data = []
        
    # popular 순위 (1페이지~ 10페이지, 페이지당 20개, 총 200개)
    
    # for i in range(1, 10):
    #     popular_url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={i}"
    #     popular = requests.get(popular_url).json()

    #     for movie in popular['results']:
    #         if movie.get("release_date") is not None:
    #             fields = {
    #                 'movie_id': movie['id'],
    #                 'title': movie['title'],
    #                 'released_date': movie['release_date'],
    #                 'rating': movie['vote_average'],
    #                 'description': movie['overview'],
    #                 'poster_path': movie['poster_path'],
    #                 'category': movie['genre_ids'],
    #                 # 'nation': movie['production_countries'],
    #                 # 'runnigtime': movie['runtime'],

    #             }

    #             data = {
    #                 "pk": movie['id'],
    #                 "model": "movies.movie",
    #                 "fields": fields
    #             }

    #             total_data.append(data)

    # with open("movie_data.json", "w", encoding="utf-8") as w:
    #     json.dump(total_data, w, indent="\\t", ensure_ascii=False)


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
    #     latest = sorted(latest_data['results'], key=lambda x:x['vote_average'], reverse=True)
       
        # print("--------------------------------")
        # pprint.pprint(latest_movie_list)
        

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
        pprint.pprint(genre_data)
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
            'page': page
        }
        
        top_rated_response = requests.get(top_rated_url, params=params)
        top_rated_data = top_rated_response.json()
        top_rated = sorted(top_rated_data['results'], key=lambda x:x['vote_average'], reverse=True)
        top_rated_movie_list.append(top_rated)
    
    context={
        'now_playing': now_playing,
        'total': total_data,
        # 'popular' : popular,
        'genre_dict' : genre_dict, 
        'genre': genre,
        # 'latest' : latest,
        'top_rated': top_rated,
        # 'latest_movie_list' : latest_movie_list,
    }
    return render(request, 'movies/index.html', context)


