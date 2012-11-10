from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
  name = models.CharField(max_length=128, db_index=True)
  year = models.IntegerField(default=0, db_index=True)
  rating = models.FloatField(default=0.0, db_index=True)
  votes = models.IntegerField(default=0, db_index=True)
  tagline = models.CharField(max_length=1024)
  description = models.TextField()
  imdb_url = models.URLField(max_length=256)
  fb_url = models.URLField(max_length=256)
  fb_likes = models.IntegerField(default=0, db_index=True)
  picture_url = models.URLField(max_length=256)

  def __unicode__(self):
    return u'Movie id={0} name={1} year={2}'.format(
        self.id, self.name, self.year
    )

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
        self.fbid, self.fname, self.lname
    )

class Seen(models.Model):
  person = models.ForeignKey(Person)
  movie = models.ForeignKey(Movie)
  rating = models.FloatField(default=0.0, null=True, blank=True)
  liked = models.BooleanField(default=False)
  review = models.TextField(null=True, blank=True, default=None)
  when_added = models.DateTimeField(auto_now_add=True)

  def __unicode__(self):
    return u'Movie id={0} seen by fbid={1}'.format(
        self.movie.id, self.person.fbid
    )
