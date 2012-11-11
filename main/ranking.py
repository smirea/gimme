from gimme.main.models import Seen

def rank_movies(movies, current_user, users):
  current_profile = current_user.get_profile()
  friend_list = list(current_profile.friends.all())
  friend_ids = [p.pk for p in friend_list]
  remove_ids = [current_profile.pk]
  remove_ids.extend(p.pk for p in users)

  person_ids = friend_ids[:] + remove_ids[:]

  output_movies = []
  for movie in movies:
    movie._watched_by = list(
      Seen.objects.filter(movie=movie,
                          person__user__in=person_ids).all())
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
    movie._score = \
        (movie.votes * movie.rating + 25000 * 7.1) / (movie.votes + 25000)
    output_movies.append(movie)

  output_movies.sort(key=lambda movie: -movie._score)
  return output_movies[:10]
