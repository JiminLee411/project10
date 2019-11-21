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
    return redirect('movies:detail', movie_pk)


def review_update_delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'PUT':
        serializer = ReviewSerializers(data=request.data, instance=review)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': '수정되었습니다.'})
    else:
        review.delete()
        return Response({'message': '삭제되었습니다.'})

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
    return redirect('movies:detail', movie_pk)
