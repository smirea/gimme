import os
import json
import os

from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from gimme.main.models import Movie, Person, Seen
from gimme.main.opengraph import Graph
from gimme.main.cinema import *
from gimme.main.nlp import process_query


def index(request):
  file_name = os.path.join(os.path.dirname(__file__),
                           '../client/index.html')
  content = open(file_name, 'rt').read()
  if request.user.is_authenticated():
    profile = request.user.get_profile()
    user_object = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'gender': profile.gender,
        'fbid': profile.fbid
    }

    content += """
<script type="text/javascript">
  var userData = %s;
</script>
""" % json.dumps(user_object)
  content += '</body></html>'
  return HttpResponse(content)

def test(request):
  user = request.user.get_profile()
  fbid = user.fbid
  #TODO: ...
  graph = Graph('AAAAAAITEghMBAPZCnBPmR1Tl7ynchZBfZArK4seZBGrZBga1vRL4fySuipXzXTevSvOf61PFypXbXAXuli1zoIVAZBBB1ZA8EYJ8MXVmB2auNHQZBNXT88EE')
  update_movies(user, graph)
  friends = graph.get_friends(fbid)
  for f in friends:
    friend_profile = Person.objects.get(fbid=f)
    update_movies(friend_profile, graph)
  return HttpResponse(json.dumps(f),
      content_type='application/json')

def update_movies(user_profile, graph):
  movies = graph.get_movies(user_profile.fbid)
  for m in movies:
    movie = Movie.get_movie(m)
    if movie != None:
      best_fit = graph.get_approximate_movie_data(m['name'])
      Seen.like_movie(user_profile, movie, best_fit)

@require_POST
def cinema(request):
  if (not 'q' in request.POST):
    raise PermissionDenied
  return HttpResponse(json.dumps(get_movie_near(request.POST['q'])),
      content_type='application/json')

@require_POST
def login_view(request):
  if (not 'fb_id' in request.POST or
      not 'fb_token' in request.POST):
    raise PermissionDenied

  fb_id = request.POST['fb_id']

  graph = Graph(request.POST['fb_token'])
  personal_data = graph.get_personal_data()

  if personal_data.get(u'id', None) != unicode(fb_id):
    raise PermissionDenied

  try:
    user_profile = Person.objects.get(fbid=fb_id)
    user_profile.update_info(personal_data)
    update_movies(user_profile, graph)
  except Person.DoesNotExist:
    user_profile = Person.create_user(personal_data)

    all_friend_data = graph.get_personal_data_multi(graph.get_friends(fb_id))
    for friend_id, friend_data in all_friend_data.iteritems():
      try:
        friend_profile = Person.objects.get(fbid=friend_id)
        friend_profile.update_info(friend_data)
        update_movies(friend_profile, graph)
      except Person.DoesNotExist:
        friend_profile = Person.create_user(friend_data)

      user_profile.friends.add(friend_profile)

  user = authenticate(username=fb_id,
                      password=Person.get_user_password(fb_id))
  login(request, user)
  return HttpResponse("OK")


@require_POST
def logout_view(request):
  logout(request)
  return HttpResponse("OK")

@login_required
def friend_list(request):
  user = request.user
  person = user.get_profile()

  data = []
  for friend in person.friends.select_related().all():
    data.append({
      "id": friend.user.id,
      "fb_id": friend.fbid,
      "name": u"{0} {1}".format(friend.user.first_name, friend.user.last_name),
    })

  return HttpResponse(json.dumps(data),
      content_type='application/json')

def query(request):
  q = request.GET.get('q', '')

  queryset = Movie.objects.all()
  if q:
    tags = request.GET.getlist('tags[]')
    tagged_profiles = User.objects.filter(id__in=tags).all()
    queryset = process_query(q, tagged_profiles, queryset)
  movies = queryset.order_by('-votes')[:10]

  data = []
  model_fields = [
    'id', 'name', 'year',
    ('rating', lambda movie: "%.1f" % movie.rating),
    'votes', 'description',
    ('taglines', lambda movie: list(movie.tagline_set.all())),
    ('likes', 'fb_likes'),
    'imdb_url', 'fb_url',
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

  return HttpResponse(json.dumps(data),
      content_type='application/json')
