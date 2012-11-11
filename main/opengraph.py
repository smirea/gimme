import urllib
import json

class Graph(object):
  base_url = 'https://graph.facebook.com'
  personal_fields = 'id,first_name,last_name,name,gender'
  movie_fields = 'id,likes,name,category,link,release_date'

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
      urllib.quote(movie_name.encode('utf8')), Graph.movie_fields, limit
    )
    data = Graph.query(url)
    data = sorted(data['data'], key=lambda x: x.get('likes', 0))
    if len(data) == 0:
      return None
    return data[-1]

  @staticmethod
  def get_movie_data(movie_id):
     url = Graph.base_url + "/{}?fields={}".format(
         movie_id, Graph.movie_fields
     )
     return Graph.query(url)


  def get_movies(self, user_id = None):
    if user_id == None:
      user_id = "me"
    url = Graph.base_url + "/{}/movies?access_token={}&fields={}".format(
        user_id,self.access_token, Graph.movie_fields
    )
    return Graph.get_data(url)

  def get_friend_data(self, friend_id):
    #TODO: replace with individual calls, then remove
    personal_data = self.get_personal_data(friend_id)
    movies = self.get_movies(friend_id)

  def get_friends(self, user_id=None):
    if user_id == None:
      user_id = "me"
    url = Graph.base_url + \
        "/{}/friends?access_token={}".format(user_id, self.access_token)
    data = Graph.get_data(url)
    return [entry['id'] for entry in data]

  def get_personal_data(self, user_id=None):
    if user_id == None:
      user_id = "me"
    url = Graph.base_url + \
        "/{}/?access_token={}&fields={}".format(
          user_id,self.access_token,Graph.personal_fields
        )
    return Graph.query(url)

  def get_personal_data_multi(self, user_ids):
    url = Graph.base_url + \
        "/?ids={}&access_token={}&fields={}".format(
            ','.join(user_ids), self.access_token, Graph.personal_fields)
    return Graph.query(url)


if __name__ == '__main__':
  access_token='AAAAAAITEghMBAPANhWj1XkPaGF6DTE8curKa5soiNZCgkB2rhaXoKW9fh1Ia9w2m3yIKUZBUCeZC38lkOMgZBSvKMrCaQtKZASgdYQhwRyFNZBONi2lsHa'
  graph = Graph(access_token)
  graph.get_approximate_movie_data('V for Vendetta')
