from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomAuthenticationForm, CustomPasswordChangeForm
from django.contrib.auth import get_user_model
from movies.models import Review, ReviewReport, Post, AdminMessage
from movies.forms import ReviewReportForm, AdminMessageForm
from django.db.models import Count
from django.http import JsonResponse
from django.db.models import F
# Create your views here.

def login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('movies:index')
    
    else:
        form = CustomAuthenticationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


@login_required
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('movies:index')


def signup(request):
    selecttags = []
   
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)        
        if form.is_valid():
            selecttags = request.POST.getlist('tag')
            user = form.save()
            auth_login(request, user)  # 회원가입 후 바로 로그인되게
            return redirect('movies:index') 
    else:
        form = CustomUserCreationForm()
        selecttags = request.POST.getlist('tag')
        
    context = {
        'form':form,
        'selecttags': selecttags,
    }
    return render(request, 'accounts/signup.html', context)


def profile(request, username):
    User = get_user_model()
    person = User.objects.get(username=username)
    reviews = Review.objects.filter(user=person)
    reports = ReviewReport.objects.values('review').annotate(num_reports=Count('review')).filter(num_reports__gte=5)
    review_ids = [report['review'] for report in reports]
    review_reports = ReviewReport.objects.order_by('review_id', 'title')
    
    # superuser일 경우 선택한 태그가 없기 때문에 태그 정보 불러오지 않음
    if person.is_superuser :
        new_tags = []
        tag_dict = []
    else:
        # 회원가입할 때 받은 tags 정보 가공 (문자열에서 리스트로 변환)
        new_tags = person.tags[2:-2].split("', '")
    
        # 내 tag와 일치하는 영화 정보 불러오기
        # my_movies = []
        tag_dict = {} 
        for tag in new_tags:
            post = Post.objects.filter(tags__contains = tag)
            for i in post:
            # my_movies.append(list(post))
                tag_dict[i] = tag
        print(tag_dict)
    # my_movies = list(set(my_movies))

    # 추가
    if request.method == 'POST':
        form = AdminMessageForm(request.POST)
        if form.is_valid():
            adminmessage = form.save(commit=False)
            adminmessage.user = request.user
            adminmessage.review_id = request.POST.get('review_id')
            adminmessage.save()
            return redirect('accounts:profile', username=username)
    else:
        form = AdminMessageForm()
        
        
    
    context = {
        'person':person,
        'reviews':reviews,
        'review_reports': review_reports,
        'new_tags': new_tags,
        # 'my_movies': my_movies,
        'tag_dict': tag_dict,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def delete(request):
    request.user.delete()
    return redirect('')


@login_required
def update(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:profile', request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/update.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('movies:index')
    else:
        form = CustomPasswordChangeForm(request.user)
    context = {
        'form':form,
    }
    return render(request, 'accounts/change_password.html', context)

@login_required
def follow(request, user_pk):
    User = get_user_model()
    person  = User.objects.get(pk=user_pk)
    me = request.user

    if person != me:
        if me in person.followers.all():
            person.followers.remove(me)
            is_followed = False
        else:
            person.followers.add(me)
            is_followed = True
        context = {
            'is_followed':is_followed,
            'followings_count':person.followings.count(),
            'followers_count':person.followers.count(),
            'followers': [{'username': f.username,'pk': f.pk} for f in person.followers.all()]

        }
        return JsonResponse(context)
    return redirect('accounts:profile', person.username)


@login_required
def followers(request, user_pk):
    User = get_user_model()
    person = User.objects.get(pk=user_pk)

    followers = [{'username': f.username, 'pk': f.pk} for f in person.followers.all()]

    context = {
        'followers': followers,
    }
    return JsonResponse(context)

def aboutus(request):
    return render(request, 'accounts/aboutus.html')
