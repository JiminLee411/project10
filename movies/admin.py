from django.contrib import admin
from .models import Genre, Movie, Review

# Register your models here.
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'audience', 'poster_url', 'description', 'genre')

admin.site.register(Genre, GenreAdmin)
admin.site.register(Movie, MovieAdmin)



