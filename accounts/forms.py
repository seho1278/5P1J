from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm,  PasswordChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth import get_user_model
import datetime

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="아이디",
        widget=forms.TextInput(
            attrs={
                'class': 'form--control',
                'placeholder': '아이디를 입력하세요',
            }
        ),
    )
    first_name = forms.CharField(
        label="이름",
        widget=forms.TextInput(
            attrs={
                'class': 'form--control',
                'placeholder': '이름을 입력하세요',
            }

        ),
    )
    birthday = forms.DateField(
        initial=datetime.date(2000, 1, 1),
        label="생일",
        widget=forms.DateInput(
            attrs={
                'type':'date',
                'class': 'form--control',
            }
        ),
    )
    email = forms.EmailField(
        label="이메일",
        widget=forms.TextInput(
            attrs={
                'class': 'form--control',

            }
        ),
    )
    image = forms.ImageField(
        label='프로필 이미지',
        required=False,
        widget=forms.ClearableFileInput(
        attrs={
            'class': 'form--control',
            }
        )
    )
    password1 = forms.CharField(
        label="비밀번호",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form--control',
                'placeholder': '비밀번호를 입력하세요',
            }
        ),
    )
    password2 = forms.CharField(
        label="비밀번호 확인",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form--control',
                'placeholder': '비밀번호를 다시 입력하세요',
            }
        ),
    )
    password=None
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = ('username', 'first_name', 'birthday', 'email', 'image')

class CustomUserChangeForm(UserChangeForm):
    email = forms.EmailField(
        label= False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '이메일을 입력하세요',
               
            }
        )
    )
    first_name = forms.CharField(
        label= False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '이름을 입력하세요',
               
            }
        )
    )
    birthday = forms.DateField(
        initial=datetime.date(2000, 1, 1),
        label=False,
        widget=forms.DateInput(
            attrs={
                'type':'date',
                'class': 'form-control',
            }
        ),
    )
    image = forms.ImageField(
        label=False,
        required=False,
        widget=forms.ClearableFileInput(
        attrs={
            'class': 'form-control',
            }
        )
    )
    password=None
    class Meta(UserChangeForm.Meta):
        model = get_user_model()
        fields = ('email', 'first_name', 'birthday', 'image')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=False,
        widget=forms.TextInput(
            attrs = {
                'class': 'login--form--control',
                'placeholder' : '아이디',
              
            }
        )
    )
    password = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs = {
                'class': 'login--form--control',
                'placeholder' : '비밀번호',
               
            }
        )
    )

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label=False,
        widget=forms.PasswordInput(
            attrs = {
                'class': 'form-control',
                'placeholder' : '기존 비밀번호',
            }
        )
    )
    new_password1 = forms.CharField(
        label=False,
        widget= forms.PasswordInput(
        attrs = {
                'class': 'form-control',
                'placeholder' : '새 비밀번호',

            }
        ),
        help_text='',
    )
    new_password2 = forms.CharField(
        label=False,
        widget= forms.PasswordInput(
        attrs = {
                'class': 'form-control',
                'placeholder' : '새 비밀번호(확인)',

            }
        ),
        help_text='',
    )