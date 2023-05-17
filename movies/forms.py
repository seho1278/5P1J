from django import forms
from django.forms import ClearableFileInput
from .models import Post, Review, Comment, ReviewReport, AdminMessage

class PostForm(forms.ModelForm):
    TAG_CHOICES = [
        ('스펙터클한', '스펙터클한'), ('빨리보고싶은', '빨리보고싶은'), ('인생이담겨있는', '인생이담겨있는'), 
        ('믿고 보는 배우인', '믿고 보는 배우인'), ('튀어나오는', '튀어나오는'),
        ('환상적인', '환상적인'), ('기승전결이 완벽한','기승전결이 완벽한'), ('외모가 잘생긴','외모가 잘생긴'), ('가슴 떨리는', '가슴 떨리는'),
        ('미장센이 좋은', '미장센이 좋은'), ('감독의 센스가 좋은', '감독의 센스가 좋은'), ('이해시켜 주는', '이해시켜 주는'), ('서정적인', '서정적인'), ('상상력이 무한한', '상상력이 무한한'),
        ('위대한 쇼인','위대한 쇼인'), ('구성이 알찬','구성이 알찬'), ('뒤끝 없는','뒤끝 없는'), ('화면 효과가 좋은','화면 효과가 좋은'), ('종결 낸','종결 낸'), ('배우들이 대거 출연한', '배우들이 대거 출연한'), ('인생의 진리를 느끼는','인생의 진리를 느끼는'), ('진심으로 응원하는','진심으로 응원하는'), ('깔쌈한', '깔쌈한'), 
        ('잘 다듬어진', '잘 다듬어진'), ('감독이 섬세한', '감독이 섬세한'), ('웃기고 재밌는', '웃기고 재밌는'), ('전개에 군더더기가 없는', '전개에 군더더기가 없는'), ('명대사를 남기는', '명대사를 남기는'), ('중간중간 놀라는', '중간중간 놀라는'), ('끝맺는', '끝맺는'), ('감독이 대단한', '감독이 대단한'), ('맨날 똑같은', '맨날 똑같은'), 
        ('노래와 춤이 있는', '노래와 춤이 있는'), ('카메오가 나오는','카메오가 나오는'), ('감독의 센스가 좋은', '감독의 센스가 좋은'), ('일확천금을 노리는', '일확천금을 노리는'), ('군더더기 없는', '군더더기 없는'), ('B급감성인', 'B급감성인'), ('아무말 대잔치인', '아무말 대잔치인'), ('갑툭튀 장면이 있는', '갑툭튀 장면이 있는'), 
        ('감독이 뚝심있는', '감독이 뚝심있는'), ('꿀 떨어지는', '꿀 떨어지는'), ('야심작인', '야심작인'), ('말 그대로 미친', '말 그대로 미친'), ('생각할 거리가 많은','생각할 거리가 많은'), ('적나라하게 보여 주는', '적나라하게 보여 주는'), ('폭력적인', '폭력적인'),
        ('상영시간이 긴', '상영시간이 긴'), ('내용이 산으로 가는', '내용이 산으로 가는'), ('난해한', '난해한'), ('지루한', '지루한'), ('무슨 소리인지 모르겠는', '무슨 소리인지 모르겠는'), ('시대착오적인', '시대착오적인'), ('결말이 부실한', '결말이 부실한'),
    ]

    tags = forms.MultipleChoiceField(
        label = '태그',
        widget = forms.CheckboxSelectMultiple(
            # attrs={
            #     'class': 'form--control',
            # }
        ),
        choices = TAG_CHOICES,

    )
    
    PLATFORM_CHOICES = [
        ('넷플릭스', '넷플릭스'), ('왓챠', '왓챠'), ('웨이브', '웨이브'), ('애플TV+', '애플TV+'), ('디즈니+', '디즈니+'),
    ]
    
    platform = forms.MultipleChoiceField(
        label = '플랫폼', 
        widget = forms.CheckboxSelectMultiple(
            # attrs = {
            #     'class': 'form--control',
            # }
        ),
        choices = PLATFORM_CHOICES,

    )

    class Meta:
        model = Post
        fields = ('platform', 'tags',)
        
class ReviewForm(forms.ModelForm):
    TAG_CHOICES = [
        ('스펙터클한', '스펙터클한'), ('빨리보고싶은', '빨리보고싶은'), ('인생이담겨있는', '인생이담겨있는'), 
        ('믿고 보는 배우인', '믿고 보는 배우인'), ('튀어나오는', '튀어나오는'),
        ('환상적인', '환상적인'), ('기승전결이 완벽한','기승전결이 완벽한'), ('외모가 잘생긴','외모가 잘생긴'), ('가슴 떨리는', '가슴 떨리는'),
        ('미장센이 좋은', '미장센이 좋은'), ('감독의 센스가 좋은', '감독의 센스가 좋은'), ('이해시켜 주는', '이해시켜 주는'), ('서정적인', '서정적인'), ('상상력이 무한한', '상상력이 무한한'),
        ('위대한 쇼인','위대한 쇼인'), ('구성이 알찬','구성이 알찬'), ('뒤끝 없는','뒤끝 없는'), ('화면 효과가 좋은','화면 효과가 좋은'), ('종결 낸','종결 낸'), ('배우들이 대거 출연한', '배우들이 대거 출연한'), ('인생의 진리를 느끼는','인생의 진리를 느끼는'), ('진심으로 응원하는','진심으로 응원하는'), ('깔쌈한', '깔쌈한'), 
        ('잘 다듬어진', '잘 다듬어진'), ('감독이 섬세한', '감독이 섬세한'), ('웃기고 재밌는', '웃기고 재밌는'), ('전개에 군더더기가 없는', '전개에 군더더기가 없는'), ('명대사를 남기는', '명대사를 남기는'), ('중간중간 놀라는', '중간중간 놀라는'), ('끝맺는', '끝맺는'), ('감독이 대단한', '감독이 대단한'), ('맨날 똑같은', '맨날 똑같은'), 
        ('노래와 춤이 있는', '노래와 춤이 있는'), ('카메오가 나오는','카메오가 나오는'), ('감독의 센스가 좋은', '감독의 센스가 좋은'), ('일확천금을 노리는', '일확천금을 노리는'), ('군더더기 없는', '군더더기 없는'), ('B급감성인', 'B급감성인'), ('아무말 대잔치인', '아무말 대잔치인'), ('갑툭튀 장면이 있는', '갑툭튀 장면이 있는'), 
        ('감독이 뚝심있는', '감독이 뚝심있는'), ('꿀 떨어지는', '꿀 떨어지는'), ('야심작인', '야심작인'), ('말 그대로 미친', '말 그대로 미친'), ('생각할 거리가 많은','생각할 거리가 많은'), ('적나라하게 보여 주는', '적나라하게 보여 주는'), ('폭력적인', '폭력적인'),
        ('상영시간이 긴', '상영시간이 긴'), ('내용이 산으로 가는', '내용이 산으로 가는'), ('난해한', '난해한'), ('지루한', '지루한'), ('무슨 소리인지 모르겠는', '무슨 소리인지 모르겠는'), ('시대착오적인', '시대착오적인'), ('결말이 부실한', '결말이 부실한'),
    ]

    tags = forms.MultipleChoiceField(
        label = '태그',
        widget = forms.CheckboxSelectMultiple(
            # attrs={
            #     'class': 'form--control',
            # }
            
        ),
        choices = TAG_CHOICES,

    )


    class Meta:
        model = Review
        exclude = ('user', 'like_users', 'post',)
        labels = {
            'content': '내용',
        }
        widgets = {
            
            'content': forms.Textarea(
                attrs={
                    'class': 'form--control',
                    'id':'Review__Writing',
                    'placeholder' : '내용을 입력해 주세요',
                    'rows':'10',
                    'style': 'border:none; background: #DBDBDB;',
                }
            ),
            
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class ReviewReportForm(forms.ModelForm):

    title = forms.ChoiceField(
        choices=ReviewReport.TITLE_CHOICES,
        label='분류(필수)',
        widget=forms.Select(
            attrs={
                'required': True,
                'class': 'form--control',
            }
        )
    )
    content = forms.CharField(
        label='허위 신고자에게는  불이익이 발생할 수 있습니다. 신고 내용을 신중하게 생각하셔서, 정확하고 상세하게 기입해 주십시오.',
        widget=forms.Textarea(
            attrs={
                'class': 'form--control',
              
            }
        )
    )
    class Meta:
        model = ReviewReport
        fields = ('title', 'content')

# 추가
class AdminMessageForm(forms.ModelForm):
    review_id = forms.IntegerField()

    class Meta:
        model = AdminMessage
        fields = ('review_id', 'content',)