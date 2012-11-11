import lxml.html
import re

class BaseCinemaUrl(object):
  BASE_PAGE = 'http://www.google.com/movies'
  
  def __init__(self, location = 'london', date = '0', movie = None):
    self.location = location
    self.date = date
    self.movie = movie

  def get_url(self):
    url = '{0}?near={1}&date={2}'.format(BaseCinemaUrl.BASE_PAGE, self.location, self.date)
    if self.movie != None:
      url += '&q={0}'.format(self.movie)
    return url

def get_movies_near(location='london', date='0'):
  url = BaseCinemaUrl(location, date).get_url()
  page = lxml.html.parse(url).getroot()
  theaters = page.xpath('//div[@class="theater"]')
  theater_to_movies = {}
  movies_to_theaters = {}
  for node in theaters:
    theater = node.xpath('div[@class="desc"]/h2[@class="name"]')[0].text_content()
    movies = [i.text_content() for i in \
        node.xpath('div[@class="showtimes"]//div[@class="movie"]/div[@class="name"]/a')]
    movies = [i for i in movies if len(i) != 0]
    theater_to_movies[theater] = movies
    for movie in movies:
      entry = movies_to_theaters.setdefault(movie, [])
      entry.append(theater)
  return (theater_to_movies, movies_to_theaters)

def get_movie_near(movie, location='london', date='0'):
  url = BaseCinemaUrl(location, date, movie).get_url()
  page = lxml.html.parse(url).getroot()
  theaters = page.xpath('//div[@class="theater"]')
  result = {}
  for theater in theaters:
    nodes = theater.xpath('div/div[@class="name"]/a')
    if len(nodes) != 0:
      place = nodes[0].text_content()
      times = theater.xpath('div[@class="times"]/span')
      final_times = []
      for t in times:
        text = t.text_content()
        res = re.findall('([0-9:]{5})', text)
        final_times.append(res[0])
      result[place] = final_times
  return result

if __name__ == '__main__':
  print get_movie_near('Argo')
