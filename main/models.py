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

  fbid = models.BigIntegerField(default=0, primary_key=True)
  fname = models.CharField(max_length=128)
  lname = models.CharField(max_length=128)
  email = models.EmailField(max_length=128)
  fburl = models.CharField(max_length=128)
  picture = models.CharField(max_length=128)
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
  rating = models.FloatField(default=0.0)
  liked = models.BooleanField(default=False)
  review = models.TextField(null=True, blank=True, default=None)

  def __unicode__(self):
    return u'Movie id={0} seen by fbid={1}'.format(
        self.movie.id, self.person.fbid
    )
