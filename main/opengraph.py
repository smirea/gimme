import urllib
import json

class Graph(object):
  base_url = 'https://graph.facebook.com'
  personal_fields = 'id,first_name,last_name,name,gender'
  movie_fields = 'id,likes,name,category'

  def __init__(self, access_token):
    self.access_token = access_token

  @staticmethod
  def query(url):
    return json.loads(urllib.urlopen(url).readlines()[0])

  @staticmethod
  def get_data(url):
    pieces = []
    while True:
      data = Graph.query(url)
      paging = data.setdefault('paging', {})
      data = data['data']
      for entry in data:
        pieces.append(entry)
      if 'next' in paging:
        url = paging['next']
      else:
        break
    return pieces

  @staticmethod
  def get_approximate_movie_data(movie_name):
    limit = 25 # hardcoded
    url = Graph.base_url + \
      "/search?q={}&type=page&fields={}&limit={}".format(
        movie_name, Graph.movie_fields, limit
    )
    data = Graph.query(url)["data"]
    data = sorted(data, key=lambda x: x["likes"])
    movie = data[-1]
    Graph.get_movie_data(movie["id"]) # print, return or model here?

  @staticmethod
  def get_movie_data(movie_id):
    url = Graph.base_url + "/{}".format(movie_id)
    data = Graph.query(url)
    print data

  def get_movies(self, user_id):
    if user_id == None:
      user_id = "me"
    url = Graph.base_url + "/{}/movies?access_token={}".format(user_id,self.access_token)
    data = Graph.get_data(url)
    movies = []
    for entry in data:
        e = {}
        e['id'] = entry.setdefault('id',0)
        e['name'] = entry.setdefault('name', None)
        e['created_time'] = entry.setdefault('created_time',None)
        movies.append(e)
    return movies

  def get_friend_data(self, friend_id):
    personal_data = self.get_personal_data(friend_id)
    movies = self.get_movies(friend_id)
    print personal_data
    print movies

  def get_my_friends(self):
    url = Graph.base_url + \
        "/me/friends?access_token={}".format(self.access_token)
    data = Graph.get_data(url)
    for entry in data:
      friend_id = entry['id']
      friend_data = self.get_friend_data(friend_id)

  def get_personal_data(self, user_id=None):
    if user_id == None:
      user_id = "me"
    url = Graph.base_url + \
        "/{}/?access_token={}&fields={}".format(
          user_id,self.access_token,Graph.personal_fields
        )
    return Graph.query(url)

  def get_my_data(self):
    personal_data = self.get_personal_data()
    movies = self.get_movies()
    print personal_data
    print movies
    self.get_my_friends()
    
if __name__ == '__main__':
  access_token='AAAAAAITEghMBAI5nVAbUg3Y9UFeUzOV51uo9fYXUQo1UyV4F9EbbeFm5XQLAlCvWsnEHVclM6A2wjznPVrvLlhCQh3HeLzc4Aoe0D0denoT1XOjb'
  graph = Graph(access_token)
  #graph.get_my_data()
  #graph.get_friend_data(1208022)
  #Graph.get_movie_data(255794484489801)
  #Graph.get_approximate_movie_data('Avengers')
