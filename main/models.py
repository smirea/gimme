import md5
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, transaction

class Movie(models.Model):
  name = models.CharField(max_length=128, db_index=True)
  year = models.IntegerField(default=0, db_index=True)
  rating = models.FloatField(default=0.0, db_index=True)
  votes = models.IntegerField(default=0, db_index=True)
  description = models.TextField()
  imdb_url = models.URLField(max_length=256)
  fb_likes = models.IntegerField(default=0, db_index=True)
  fbid = models.BigIntegerField(default=0)

  @staticmethod
  def get_movie(movie_data):
    year = movie_data.get('release_date', '')
    years = re.findall('([0-9]{4})', year)
    if len(years) > 0:
      year = int(years[0])
    else:
      year = 0
    res = Movie.objects.filter(name__icontains=movie_data['name'])
    if year != 0:
      res = res.filter(year__gt=year-2).filter(year__lt=year+2)
    res = res.order_by('-votes')
    results = res.all()
    if len(results) > 0:
      return results[0]
    else:
      return None

  def __unicode__(self):
    return u'Movie id={0} name={1} year={2}'.format(
        self.id, self.name, self.year
    )

class Tagline(models.Model):
  movie = models.ForeignKey(Movie) 
  line = models.CharField(max_length=256)

class Genre(models.Model):
  name = models.CharField(max_length=64)

  genre_movies = models.ManyToManyField(
      Movie,
      related_name="movie_genres"
  )

  def __unicode__(self):
    return u'Genre id={0} name={1}'.format(
        self.id, self.name
    )

class Person(models.Model):
  MALE = 0
  FEMALE = 1
  GENDER = (
    (MALE, 'Male'),
    (FEMALE, 'Female'),
  )

  user = models.OneToOneField(User, primary_key=True)
  fbid = models.BigIntegerField(default=0)
  gender = models.IntegerField(choices=GENDER, default=MALE)

  friends = models.ManyToManyField("self")
  rated_movies = models.ManyToManyField(
      Movie,
      through='Seen'
  )

  def __unicode__(self):
    return u'Person fbid={0} fname={1} lname={2}'.format(
        self.fbid, self.user.first_name, self.user.last_name
    )

  @staticmethod
  @transaction.commit_on_success
  def create_user(personal_data):
    user = User(username=personal_data[u'id'],
                first_name=personal_data.get(u'first_name', ''),
                last_name=personal_data.get(u'last_name', ''),
                email=personal_data.get(u'email', ''))
    user.set_password(Person.get_user_password(personal_data[u'id']))
    user.save()

    profile = Person(user=user)
    profile.fbid = personal_data[u'id']
    if u'gender' in personal_data:
      if personal_data[u'gender'] == 'male':
        profile.gender = Person.MALE
      elif personal_data[u'gender'] == 'female':
        profile.gender = Person.FEMALE
    profile.save()

    return profile

  @transaction.commit_on_success
  def update_info(self, personal_data):
    user = self.user

    if u'first_name' in personal_data:
      user.first_name = personal_data[u'first_name']
    if u'last_name' in personal_data:
      user.last_name = personal_data[u'last_name']
    if u'email' in personal_data:
      user.email = personal_data[u'email']
    user.save()

    if u'gender' in personal_data:
      if personal_data[u'gender'] == 'male':
        self.gender = Person.MALE
      elif personal_data[u'gender'] == 'female':
        self.gender = Person.FEMALE
      self.save()

  @staticmethod
  def get_user_password(fb_id):
    m = md5.new()
    m.update(fb_id)
    m.update(settings.SECRET_KEY)
    return m.hexdigest()

class Seen(models.Model):
  person = models.ForeignKey(Person)
  movie = models.ForeignKey(Movie)
  rating = models.FloatField(default=0.0, null=True, blank=True)
  liked = models.BooleanField(default=False)
  review = models.TextField(null=True, blank=True, default=None)
  when_added = models.DateTimeField(auto_now_add=True)

  @staticmethod
  @transaction.commit_on_success
  def like_movie(user, movie, movie_data):
    seen = Seen(person=user,movie=movie,liked=True)
    seen.save()

    fbid = movie_data.get(u'id',None) 
    if fbid != None:
      movie.fbid = fbid
    movie.fb_likes = movie_data.get(u'likes', 0)
    movie.save()


  def __unicode__(self):
    return u'Movie id={0} seen by fbid={1}'.format(
        self.movie.id, self.person.fbid
    )
