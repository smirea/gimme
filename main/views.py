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
from gimme.main.ranking import rank_movies


def index(request):
  file_name = os.path.join(os.path.dirname(__file__),
                           '../client/index.html')
  content = open(file_name, 'rt').read()
  if request.user.is_authenticated():
    #TODO: this seems broken..
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
  #TODO: this seems broken
  #TODO: mb look into fixing this so that we get friend's movies
  #user = request.user.get_profile()
  #fbid = user.fbid
  #TODO: UNHACK
  fbid = 100000003935672
  user_profile = Person.objects.get(fbid=fbid)
  graph = Graph('AAAAAAITEghMBALnZCyaZBHvSHmcjOCffC2nZA4vrLG0aRh9ZCDpNMW7YnGLBmzWPZBRQ3VAazIdvh0SCxRQuLbiOOAe2LS44gIj2ymTg0QuuNUHZCSu1Yr')

  update_movies(user_profile, graph)
  friends = graph.get_friends(fbid)
  for f in friends:
    friend_profile = Person.objects.get(fbid=f)
    update_movies(friend_profile, graph)
  return HttpResponse(json.dumps(friends),
      content_type='application/json')

def update_movies(user_profile, graph):
  movies = graph.get_movies(user_profile.fbid)
  for m in movies:
    movie = Movie.get_movie(m)
    if movie != None:
      best_fit = graph.get_approximate_movie_data(m['name'])
      if best_fit != None:
        Seen.like_movie(user_profile, movie, best_fit)

def cinema(request):
  if (not 'q' in request.GET):
    raise PermissionDenied
  days = {}
  for i in xrange(4):
    days[i] = get_movie_near(request.GET['q'], date=i)
  return HttpResponse(json.dumps(days), content_type='application/json')

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
  except Person.DoesNotExist:
    user_profile = Person.create_user(personal_data)
    update_movies(user_profile, graph)

    all_friend_data = graph.get_personal_data_multi(graph.get_friends(fb_id))
    for friend_id, friend_data in all_friend_data.iteritems():
      try:
        friend_profile = Person.objects.get(fbid=friend_id)
        friend_profile.update_info(friend_data)
      except Person.DoesNotExist:
        friend_profile = Person.create_user(friend_data)
        update_movies(friend_profile, graph)

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
    queryset, tagged_profiles = process_query(q, tagged_profiles, queryset)
  movies = rank_movies(queryset.order_by('-votes')[:100],
                       request.user, tagged_profiles)

  data = []
  model_fields = [
    'id', 'name', 'year',
    ('rating', lambda movie: "%.1f" % movie.rating),
    'votes', 'description',
    ('taglines', lambda movie: [tagline.line for tagline
                                in movie.tagline_set.all()]),
    ('likes', 'fb_likes'),
    'imdb_url', 'fbid',
    ('genres', lambda movie: [genre.name for genre
                              in movie.movie_genres.all()]),
    ('friends_recommended', lambda movie: movie._friend_recommend),
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
