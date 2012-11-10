import json

from django.http import HttpResponse

from gimme.main.models import Movie


def example(request):
  return HttpResponse("Hello, world!")


def query(request):
  q = request.GET.get('q', '')

  queryset = Movie.objects.all()
  if q:
    queryset = queryset.filter(name__contains=q)
  movies = queryset.order_by('-rating')[:10]

  data = []
  model_fields = [
    'id', 'name', 'year', 'rating', 'votes', 'tagline', 'description',
    ('likes', 'fb_likes'), 'imdb_url', 'fb_url',
    ('genres', lambda movie: [genre.name for genre
                              in movie.movie_genres.all()]),
    ('picture', 'picture_url'),
    ('friends_recommended', lambda movie: 0),
    ('guru', lambda movie: None)
  ]

  for movie in movies:
    movie_dict = {}
    for field in model_fields:
      if isinstance(field, tuple):
        if callable(field[1]):
          movie_dict[field[0]] = field[1](movie)
        else:
          movie_dict[field[0]] = getattr(movie, field[1])
      else:
        movie_dict[field] = getattr(movie, field)
    data.append(movie_dict)

  return HttpResponse(json.dumps(data))
