import math

from gimme.main.models import Seen

def rank_movies(movies, current_user, users):
  current_profile = current_user.get_profile()
  friend_list = list(current_profile.friends.all())
  friend_ids = [p.pk for p in friend_list]
  remove_ids = [current_profile.pk]
  remove_ids.extend(p.pk for p in users)

  person_ids = set(friend_ids) | set(remove_ids)

  output_movies = []
  for movie in movies:
    movie._watched_by = list(
      Seen.objects.filter(movie=movie,
                          person__user__in=person_ids).select_related('person',
                            'person__user').all())
    movie._should_skip = False
    movie._friend_recommend = []
    for seen in movie._watched_by:
      if seen.liked and seen.person_id in friend_ids:
        movie._friend_recommend.append({
          'id': seen.person.user.id,
          'fbid': seen.person.fbid,
          'name': u'{0} {1}'.format(seen.person.user.first_name,
                                    seen.person.user.last_name)
        })

      if seen.person_id in remove_ids:
        movie._should_skip = True

    if movie._should_skip:
      continue

    """
    if movie.fb_likes == 0:
      best_fit = Graph.get_approximate_movie_data(movie.name)
      if best_fit != None:
        fb_likes = best_fit.get('fb_likes', 0)
    """
    
    imdb_rating = (movie.votes * movie.rating + 25000 * 7.1) / (movie.votes + 25000)
    if movie.fb_likes == 0:
      like_rating = 6
    else:
      like_rating = (math.log(movie.fb_likes+1.0)/2.0) 
    friend_rating = (math.atan(0.28 * len(movie._friend_recommend)))

    movie._score = imdb_rating + like_rating + friend_rating

    output_movies.append(movie)

  output_movies.sort(key=lambda movie: -movie._score)
  return output_movies[:10]
