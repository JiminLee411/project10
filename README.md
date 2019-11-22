# Project 10 - Pair Programming

## 1. 목표

> Pair Coding을 통한 데이터베이스를 모델링 및 영화 목록 및 상세 페이지, 유저 목록 및 상세 페이지, 좋아요 기능 구현



## 2. 설계

### 1. DB 설계

* `accounts/models.py`

  ```python
  from django.db import models
  from django.contrib.auth.models import AbstractUser
  from django.conf import settings
  
  # Create your models here.
  class User(AbstractUser):
      followings = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)
  ```
  
* `movies/models.py`

  ```python
  from django.db import models
  from django.conf import settings
  
  # Create your models here.
  class Genre(models.Model):
      name = models.CharField(max_length=20)
  
  class Movie(models.Model):
      title = models.CharField(max_length=30)
      audience = models.IntegerField()
      poster_url = models.CharField(max_length=140)
      description = models.TextField()
      genres = models.ManyToManyField(Genre)
      like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="like_movies")
  
  
  
  class Review(models.Model):
      content = models.CharField(max_length=140)
      score = models.IntegerField()
      movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  ```

* 데이터 베이스 반영한 뒤, `makemigrations` / `migrate`

### 2. Seed Data 반영

* `movie.json`과 `genre.json`를 반영한뒤, `admin.py`에 `Genre`와 `Movie`클래스 등록

  ```bash
  $ python manage.py loaddata genre.json
  $ python manage.py loaddata movie.json
  ```

  `fixtures`폴더안에 `json`파일들을 넣어준다.

  

* `admin.py`를 통해서 실제로 DB에 반영한다.

  ```python
  from django.contrib import admin
  from .models import Genre, Movie
  
  class GenreAdmin(admin.ModelAdmin):
      list_display = ('id', 'name')
  
  class MovieAdmin(admin.ModelAdmin):
      list_display = ('id', 'title', 'audience', 'poster_url', 'description',)
  
  admin.site.register(Genre, GenreAdmin)
  admin.site.register(Movie, MovieAdmin)
  ```

### 3. Form 설계

* `accounts/forms.py`

  ```python
  from django.contrib.auth import get_user_model
  from django.contrib.auth.forms import UserCreationForm, UserChangeForm
  
  class CustomUserCreationForm(UserCreationForm):
      class Meta:
          model = get_user_model()
          fields = ('username', )
  
  class CustomUserChangeForm(UserChangeForm):
      class Meta:
          model = get_user_model()
          fields = ('username', )
  ```

* `movies/forms.py`

  ```python
  from django import forms
  
  from .models import Review
  
  class ReviewForm(forms.ModelForm):
      class Meta:
          model = Review
          fields = ('content', 'score')
  ```

### 4. URL 설정

* `pjt10/urls.py`

  ```python
  from django.contrib import admin
  from django.urls import path, include
  
  urlpatterns = [
      path('admin/', admin.site.urls),
      path('accounts/', include('accounts.urls')),
      path('movies/', include('movies.urls'))
  ]
  ```

* `accounts/urls.py`

  ```python
  from django.urls import path
  from . import views
  
  app_name = 'accounts'
  
  urlpatterns = [
      path('', views.index, name="index"),
      path('signup/', views.signup, name='signup'),
      path('login/', views.login, name='login'),
      path('logout/', views.logout, name='logout'),
      path('<int:user_pk>/', views.detail, name="detail"),
      path('<int:user_pk>/follow/', views.follow, name='follow'),
  ]
  ```

* `movies/urls.py`

  ```python
  from django.urls import path
  from . import views
  
  app_name = 'movies'
  
  urlpatterns = [
      path('', views.movies_index, name='movies_index'),
      path('<int:movie_pk>/', views.movies_detail, name='movies_detail'),
      path('<int:movie_pk>/reviews/new/', views.review_create, name='review_create'),
      path('<int:movie_pk>/reviews/<int:review_pk>/delete/', views.review_delete, name='review_delete'),
      path('<int:movie_pk>/like/', views.like, name='like')
  ]
  ```



### 5. View 정의

* `accounts/views.py`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from django.contrib.auth import get_user_model
  from django.contrib.auth.decorators import login_required
  from .forms import CustomUserChangeForm, CustomUserCreationForm
  from django.contrib.auth import login as auth_login
  from django.contrib.auth import logout as auth_logout
  from django.contrib.auth.forms import AuthenticationForm
  # Create your views here.
  def index(request):
      context = {
          'users' : get_user_model().objects.all()
      }
      return render(request, 'accounts/index.html', context)
  
  def signup(request):
      if request.method == 'POST':
          form = CustomUserCreationForm(request.POST)
          if form.is_valid():
              auth_login(request, form.save())
              return redirect('accounts:index')
      else:
          form = CustomUserCreationForm
      context = {
          'form': form
      }
      return render(request, 'accounts/form.html', context)
  
  def detail(request, user_pk):
      context = {
          'user_profile' : get_user_model().objects.get(pk=user_pk)
      }
      return render(request, 'accounts/detail.html', context)
  
  def login(request):
      if request.user.is_authenticated:
          return redirect('accounts:index')
      if request.method == 'POST':
          form = AuthenticationForm(request, request.POST)
          if form.is_valid():
              auth_login(request, form.get_user())
              return redirect('accounts:index')
      else:
          form = AuthenticationForm()
      context = {
          'form': form
      }
      return render(request, 'accounts/form.html', context)
  
  def logout(request):
      auth_logout(request)
      return redirect('accounts:index')
  
  @login_required
  def follow(request, user_pk):
      user = get_object_or_404(get_user_model(), pk=user_pk)
      if request.user != user:
          if user in request.user.followers.all():
              request.user.followers.remove(user)
          else:
              request.user.followers.add(user)
      return redirect('accounts:detail', user_pk)
  ```

* `movies/views.py`

  ```python
  from django.shortcuts import render, redirect, get_object_or_404
  from .models import Genre, Movie, Review
  from django.views.decorators.http import require_POST
  from django.contrib.auth.decorators import login_required
  from .forms import ReviewForm
  # from django.contrib import messages
  
  # Create your views here.
  def movies_index(request):
      movies = Movie.objects.all()
      context = {
          'movies' : movies
      }
      return render(request, 'movies/movies_index.html', context)
  
  def movies_detail(request, movie_pk):
      movie = get_object_or_404(Movie, pk=movie_pk)
      form = ReviewForm()
      context = {
          'movie': movie,
          'form': form
      }
      return render(request, 'movies/movies_detail.html', context)
  
  @require_POST
  def review_create(request, movie_pk):
      if request.user.is_authenticated:
          form = ReviewForm(request.POST)
          if form.is_valid():
              review = form.save(commit=False)
              review.user = request.user
              review.movie_id = movie_pk
              review.save()
      else:
          messages.warning(request, '로그인이 필요합니다.')
      return redirect('movies:movies_detail', movie_pk)
  
  
  def review_delete(request, review_pk):
      review = get_object_or_404(Review, pk=review_pk)
      review.delete()
      messages.warning(request, '리뷰가 삭제되었습니다.')
      return redirect('movies:movies_detail', movie_pk)
  
  @require_POST
  def like(request, movie_pk):
      movie = get_object_or_404(Movie, pk=movie_pk)
      if request.user.is_authenticated:
          if movie in request.user.like_movies.all():
              request.user.like_movies.remove(movie)
          else:
              request.user.like_movies.add(movie)
      else:
          messages.warning(request, '로그인이 필요한 기능입니다.')
      return redirect('movies:movies_detail', movie_pk)
  ```



## 3. 느낀점

> 함께 협업을 하며 다양한 기능을 이용해 볼 수 있었습니다.
>
> * fork를 이용하여 코드를 병합하였고
> * trello를 이용하여 서로 현 상황과 필요한 부분을 공유할 수 있었습니다.
>
> 다양한 git error를 마주하며
>
> * db.sqlite는 꼭 `.gitignore`에 넣어야 한다는 점과
> * checkout을 이용하여 다양한 경로로 이동이 가능하다는 것을 배울 수 있었습니다.