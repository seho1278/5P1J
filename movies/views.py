from django.shortcuts import render, redirect
from .models import Post, Review, Comment, ReviewReport, AdminMessage
from .forms import PostForm, ReviewForm, CommentForm, ReviewReportForm
import os, json
import requests
import pprint
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from collections import Counter
import concurrent.futures
from django.views.decorators.cache import cache_page
# Create your views here.

# 리뷰 평균 계산모듈(추가)
from django.db.models import Avg

TMDB_API_KEY = 'dfc02edc73a8a31017aeb0d746f5753d'

# 추가
TAG_CHOICES_DICT = {
    '컨셉 & 아이디어': [
        '무슨 생각인지 알 수 없는',
        '해석이 새로운',
        '누구나 이해할 수 있는',
        '개성있는',
        '유쾌함을 잃지 않는',
        '상상력이 무한한',
    ],
    '작품성':[
        '러블리한', 
        '영양가 없는', 
        '모던한', 
        '취향을 저격하는', 
        '옛날 감성인', 
        'B급감성인', 
        '친구들끼리 보는', 
        '애인이랑 보는', 
        '완성도가 높은', 
        '언제 봐도 좋은', 
        '내 눈을 의심하는', 
        '전혀 유쾌하지 않은',
    ],
    '캐릭터':[
        '캐릭터가 사랑스러운', 
        '개 잘생긴', 
        '개 예쁜', 
        '띨띨한', 
        '끼부리는', 
        '쥐어박고 싶은', 
        '호구인', 
        '개새끼인', 
        '암걸리는', 
        '천재인', 
        '동물이 주인공인',
    ],
    '감상평':[
        '읭스러운', 
        '감탄사를 연발하는', 
        '보는 내내 설레는', 
        '웃음이 떠나지 않는', 
        '깜놀하는', 
        '거부감 드는', 
        '경악하는', 
        '추억을 자극하는', 
        '박장대소 하는', 
        '리뷰를 찾아보는', 
        '엄청난 충격을 받는', 
        '지루 할 수 있는',
    ],
    '감독 & 연출':[
        '거장의 작품인', 
        '구닥다리인', 
        '레트로한', 
        '특유의 매력이 있는', 
        '기술적인 성취를 보인', 
        '장인정신인', 
        '거침없는', 
        '미친 연출력인', 
        '감독에게 찬사를 보내는', 
        '연출이 과감한',
    ],
    '스토리 & 구성':[
        '인생이 담겨있는', 
        '내용 별거 없는',
        '두서없는',
        '급발진하는', 
        '막장 드라마인', 
        '완급 조절에 실패한', 
        '내용이 뻔한',
        '결말이 뻔히 보이는',
        '내용이 알찬',
        '속도감 있는',
        '권선징악인',
        '반전의 묘미가 있는',
        '꼬이고 꼬인',   
        '전개가 깔끔한',
    ],
    '편집 & 각본':[
        '의식의 흐름',    
        '유행어를 낳은',
        '가벼운 농담을 던지는',
        '클리셰를 깨는',    
        '말장난을 하는',
        '빌드업한',    
        '문학적인',
    ],
    '시각 & 음향':[
        '구경하는 재미가 있는',
        '블링블링한',
        '색감이 다채로운',    
        '특유의 색감이 있는',
        '화려한',
        '영상미가 세련된',
        '마법 같은',
        '음악이 조화를 이루는',
        '한 폭의 그림 같은',
        '비주얼 쇼크인',
    ],
    '클라이맥스 & 결말':[
        '클라이맥스',
        '마무리가 훈훈한',
        '극적인 피날레',
        '예상치 못한 결말',
        '마무리가 훈훈한',
        '주인공이 행복해지는',
        "열린결말인",
        '결말이 마음에 드는',
        '황급한',
    ],        
}

# 리뷰 평균 계산(추가)
def calculate_average_rating(reviews):
    average_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    return average_rating


def fetch_movie_data(movie):
    movie_id = movie.movie_id
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=ko-KR'
    response = requests.get(url)
    movie_data = response.json()
    poster_path = 'https://image.tmdb.org/t/p/w200' + movie_data.get('poster_path')
    movie.poster_path = poster_path


@cache_page(60 * 15) # 15분동안 캐싱유지
def main(request):
    # 각 영화의 리뷰 평점
    movies = Post.objects.annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for movie in movies:
            future = executor.submit(fetch_movie_data, movie)
            futures.append(future)
        # 모든 API 호출이 완료될 때까지 기다립니다.
        concurrent.futures.wait(futures)

    # 플랫폼 별 리뷰 평점 순서
    platforms = ['넷플릭스', '왓챠', '웨이브', '애플TV+', '디즈니+']
    movies_by_platform = {}
    for platform in platforms:
        platform_movies = Post.objects.filter(platform__contains=platform).annotate(avg_rating=Avg('review__rating')).order_by('-avg_rating')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for platform_movie in platform_movies:
                future = executor.submit(fetch_movie_data, platform_movie)
                futures.append(future)
            concurrent.futures.wait(futures)
        movies_by_platform[platform] = platform_movies
    
    # 장르별로
    genre_dict = {
        28: '액션',
        12: '모험',
        16: '애니메이션',
        35: '코미디',
        80: '범죄',
        99: '다큐멘터리',
        18: '드라마',
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

    genre_movie_url = 'https://api.themoviedb.org/3/discover/movie'
    params = {
    'api_key': TMDB_API_KEY,
    'language': 'ko-kr',
    'region':'kr',
    }

    genre_movie_data = {}

    for genre_id, genre_name in genre_dict.items():
        genre_movies = []
        params['with_genres'] = genre_id
        genre_movie_response = requests.get(genre_movie_url, params=params)
        genre_movie_data[genre_name] = genre_movie_response.json()
        genre_movies.extend(genre_movie_data[genre_name]['results'])

        for genre_movie in genre_movies:
            if 'poster_path' in genre_movie:
                poster_path = genre_movie['poster_path']
                genre_poster_path = 'https://image.tmdb.org/t/p/w200' + poster_path
                genre_movie['poster_path'] = genre_poster_path

        # Only save up to 5 movies
        genre_movie_data[genre_name]['results'] = genre_movies[:5]

    
    # 장르별로 평점순으로 정렬
    for genre_name, movies_data in genre_movie_data.items():
        genre_movies = movies_data['results']
        sorted_movies = sorted(genre_movies, key=lambda movie: movie['vote_average'], reverse=True)
        genre_movie_data[genre_name]['results'] = sorted_movies

    context = {
        'movies':movies,
        'movies_by_platform':movies_by_platform,
        'genre_movie_data':genre_movie_data,
    }
    return render(request, 'movies/main.html', context)

@login_required
def index(request):   
    my_tags = []
    tag_dict = {}
    reviewed_posts = []
    if request.user.is_superuser :
        pass
    else:
        if request.user.is_authenticated:
            my_tags = request.user.tags[2:-2].split("', '")


            # print(my_tags)
    
        # 내 tag와 일치하는 영화 정보 불러오기
        for tag in my_tags:
            # print(tag)
            posts = Post.objects.filter(tags__contains = tag)
            reviews = Review.objects.filter(tags__contains = tag)
            reviews_posts = [review.post for review in reviews]
            reviewed_posts = list(set(list(posts) + reviews_posts))
            i_list = []
            for i in reviewed_posts :
                i_list.append(i)
                tag_dict[tag] = i_list
        # print(reviewed_posts)
        # print(tag_dict)

        
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
        'genre_movie_list' : genre_movie_list,
        'tag_dict': tag_dict,
        'reviewed_posts': reviewed_posts,
        # 추가
        'my_tags': my_tags,
        'TAG_CHOICES_DICT': TAG_CHOICES_DICT,
       
    }
    return render(request, 'movies/index.html', context)



@login_required
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
    
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=ko-kr'
    credits_response = requests.get(credits_url)
    credits_data = credits_response.json()
    credits = credits_data['cast'][:6]
    profile_path = 'https://image.tmdb.org/t/p/w200'

     # platform 하나씩 빼내기 
    platform_list = []
    # 수정
    if post is not None and "[" in post.platform:
        platform_word = ""
        #---------------------------
        for platform in post.platform:
            if platform in ["[", "'",]:
                pass
            elif platform in [",", "]"]:
                platform_list.append(platform_word.strip())
                platform_word = ""
            else:
                platform_word = platform_word + platform
    else:
        # 수정
        platform_list = []
        # platform_list.append(post.platform)
    
    # post에 있는 tags 하나씩 빼내기
    p_tags = []
    # 수정
    if post is not None and "[" in post.tags:
        p_word = ""
        # ------------------------
        for tag in post.tags:    
            if tag in ["[", "'",]:
                pass
            elif tag in [",", "]"]:
                p_tags.append(p_word.strip())
                p_word = ""
            else:
                p_word = p_word + tag
    else:
        # 수정
        p_tags = []
        # p_tags.append(post.tags)
        
    
    # reviews에 있는 tags 하나씩 빼내기
    tags = []
    # 추가------
    r_tags = {}
    cnt = 1
    # ----------
    word = ""
    reviews = Review.objects.filter(post=post.pk)   
    for review in reviews:
        # 추가
        tags1 = []
        #----------
        # 수정
        if review.tags is not None and  "[" in review.tags:
            for tag in review.tags:    
                if tag in ["[", "'",]:
                    pass
                elif tag in [",", "]"] :
                    tags.append(word.strip())
                    # 추가
                    tags1.append(word.strip())
                    # -------------------
                    word = ""
                    
                else:
                    word = word + tag
            # 추가
            r_tags[cnt] = tags1
            cnt += 1
            # ---------------------
        # 수정
        elif review.tags is not None:
            tags.append(review.tags)
    
    # 추가
    r_tags_list = []
    for value in r_tags.values():
        r_tags_list.append(value)
    # ---------------------------
    
    total = p_tags + tags
    total_tags = dict(Counter(total)) 
    total_tags = dict(sorted(total_tags.items(), key=lambda x: x[1], reverse=True))
    
    # print(total_tags)

    detail_response = requests.get(detail_url, params=params)
    detail_data = detail_response.json()
    
    # 추가
    average = detail_data['vote_average']/2

    average_rating = calculate_average_rating(reviews)
    # ------------------------------------

    similar_response = requests.get(similar_url, params=params)
    similar_data = similar_response.json()
    similars = sorted(similar_data['results'], key=lambda x:x['vote_average'], reverse=True)
   
    
    context = {
        'detail_data':detail_data,
       # 'keyword_data': keyword_data,
        'movie_id' : movie_id,
        'post': post,
        'similars' : similars,
        'reviews': reviews,
        'tags' : tags,
        'p_tags' : p_tags,
        'platform_list': platform_list,
        'total_tags': total_tags,
        # 추가
        'r_tags_list': r_tags_list,
        'average': average,
        'average_rating': average_rating,
        # ----------------------------
        'credits': credits,
        'profile_path': profile_path,
       
        
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
    # pprint.pprint(search_data)
    
    person_response = requests.get(person_url, params=params)
    person_search_data = person_response.json()
    

    tag_movies = Post.objects.filter(tags__contains=query)
    tag_reviews = Review.objects.filter(tags__contains=query)   
    
    tag_name = ''
    for movie in tag_movies :
        word = movie.tags[2:-2]
        word = word.split("', '")
        
        for tag in word :
            if query in tag:
                tag_name = tag
            
    # tag_reviews에서 post 역참조 후 중복 제거 
    tag_reviews_1 = list(set([review.post for review in tag_reviews])) 
    
    # tag_movies와 tag_reviews_1 에서 중복 제거 후 총 영화 수 산출 
    total_tags = len(list(set(list(tag_movies) + tag_reviews_1)))

    
    # print(tag_movies)
    # print('----')
    # print(tag_reviews)
    # print('----')
    # print(tag_reviews_1)
    # print(len(search_data))
    
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
    
    posts = sorted(search_data['results'], key=lambda x: x['release_date'], reverse=True)
    
    # page = request.GET.get('page', '1')
    # per_page = 12
    # paginator = Paginator(sorted_data, per_page)
    # posts = paginator.get_page(page)
    
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
        'tag_movies': tag_movies,
        'tag_reviews': tag_reviews,
        'tag_reviews_1' : tag_reviews_1,
        'total_tags' : total_tags,
        'tag_name' : tag_name,
    }
    
    return render(request, 'movies/search.html', context)

@login_required
def create(request, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=ko-KR'
    response = requests.get(url)
    movie_data = response.json()
    # poster_path = 'https://image.tmdb.org/t/p/w200' + movie_data.get('poster_path')
    # if request.user != 'admin':
    #     return redirect('movies:index')
    
    # selecttags = []
    if Post.objects.filter(movie_id=movie_id).exists():
        return redirect('movies:index')
    
    else:
        if request.user.is_superuser:
            if request.method == 'POST':
                form = PostForm(request.POST)
                selecttags = []
                if form.is_valid():
                    post = form.save(commit=False)
                    post.movie_id = movie_id
                    post.user = request.user
                    post.poster_path = movie_data.get('poster_path')
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
                selecttags = request.POST.getlist('tag')

            context = {
                'form': form,
                'movie': movie_data,
                'selecttags' : selecttags,
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
    # movie = get_movie_info(movie_id)
    
    post = Post.objects.get(movie_id=movie_id)
    # post = Post.objects.get(pk=post_pk)
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
        selecttags = request.POST.getlist('tag')
        
    # print(selecttags)
    context = {
        'form': form,
        'post': post,
        'selecttags': selecttags,
    }
    
    return render(request, 'movies/review_create.html', context)

@login_required
def review_delete(request, movie_id, review_id):
    # 수정
    review = Review.objects.get(id=review_id)
    referer = request.META.get('HTTP_REFERER')

    # 추가
    if request.user == review.user or request.user.is_superuser:
        review.delete()
        if referer and 'profile' in referer:
            return redirect('accounts:profile', username=request.user.username)
        else:
            return redirect('movies:detail', movie_id)
    
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
    'review_likes_count': review.like_users.count()
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
    return render(request, 'movies/review_detail.html', context)

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
            review.user.reported = True
            review.user.save()
            # 추가
            review.report = True
            review.save()
            return redirect('movies:detail', movie_id)
            
    context = {
        'review': review,
        'form': form,
        'movie_id' : movie_id,
        'review_id' : review_id,
    }
    return render(request, 'movies/review_report.html', context)


@login_required
def comment_like(request, movie_id, review_id, comment_id):
    comment = Comment.objects.get(id=comment_id)

    if comment.like_users.filter(pk=request.user.pk).exists():
        comment.like_users.remove(request.user)
        is_liked = False
    else:
        comment.like_users.add(request.user)
        is_liked = True

    data = {
        'is_liked': is_liked,
        'comment_like_count': comment.like_users.count()
    }
    return JsonResponse(data)


