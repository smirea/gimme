# Natural Language Processing for the win.

import re

from gimme.main.models import Genre

def process_query(query, tags, input_query_set):
  query_set = input_query_set

  # Remove tagged users from query
  actual_tags = []
  for tag in tags:
    regex = re.compile(re.escape(u'@{0} {1}'.format(tag.first_name,
                                                    tag.last_name)) +
                       u'(\W|$)')
    (query, nr) = regex.subn(u'\g<1>', query)
    if nr != 0:
      actual_tags.append(tag)
  tags = actual_tags
  query = re.sub('\s+', ' ', query).strip()
  query = query.lower()
  if len(tags):
    if query.endswith(' include'):
      query = query[:-8].strip()
    elif query.endswith(' with'):
      query = query[:-5].strip()

  # Regular expressions for matching complex year queries
  year_groups = ["twenty", "thirty", "fourty", "fifty", "sixty", "seventy",
                 "eighty", "ninety"]
  year_fragment = '|'.join(
      ["the {0}'s".format(year_group) for year_group in year_groups] +
      ['the {0}ies'.format(year_group[:-1]) for year_group in year_groups] +
      ['the \d{2}s', 'the \d{4}s', '\d{4}'])
  year_regex = re.compile(
      '(from ({0})|from before ({0})|from after ({0}))$'.format(year_fragment))
  def process_year(year):
    if re.match('^\d{4}$', year):
      year = int(year)
      return year, year
    matches = re.match('^the (\d{3})\ds$', year)
    if matches:
      group = int(matches.group(1)) * 10
      return group, group + 9
    matches = re.match('^the (\d)\ds$', year)
    if matches:
      group = 1900 + int(matches.group(1)) * 10
      return group, group + 9

    cur_group = 20
    for year_group in year_groups:
      if year == "the {0}'s".format(year_group):
        return 1900 + cur_group, 1909 + cur_group
      if year == "the {0}ies".format(year_group[:-1]):
        return 1900 + cur_group, 1909 + cur_group
      cur_group += 10

    return None, None

  # Rating constraint regex
  rated_regex = re.compile("(rated below \d(\.\d)?|rated above \d(\.\d)?)$")

  # name_fragment = "\w+\W+\w+"
  # with_actor_regex = re.compile("starring " + name_fragment)
  # with_director_regex = re.compile("directed by " + name_fragment)

  done = False
  # Check the end of the string for matching constraints:
  # years, ratings, actors, directors

  # Makes the assumption that the name of the movie or the genre is the first
  # thing the user specifies
  while not done:
    done = True

    year_constraint = year_regex.search(query)
    if year_constraint:
      query = year_regex.sub('', query).strip()
      year_constraint = year_constraint.group()
      assert year_constraint.startswith('from ')
      year_constraint = year_constraint[5:]

      if year_constraint.startswith('after '):
        year_lower, year_upper = process_year(year_constraint[6:])
        year_lower, year_upper = year_upper + 1, None
      elif year_constraint.startswith('before '):
        year_lower, year_upper = process_year(year_constraint[7:])
        year_lower, year_upper = None, year_lower - 1
      else:
        year_lower, year_upper = process_year(year_constraint)

      if year_lower:
        query_set = query_set.filter(year__gte=year_lower)
      if year_upper:
        query_set = query_set.filter(year__lte=year_upper)
      done = False

    rated_constraint = rated_regex.search(query)
    if rated_constraint:
      query = rated_regex.sub('', query).strip()
      rated_constraint = rated_constraint.group()
      assert rated_constraint.startswith('rated ')
      rated_constraint = rated_constraint[6:]

      if rated_constraint.startswith('above '):
        query_set = query_set.filter(rating__gte=float(rated_constraint[6:]))
      else:
        assert rated_constraint.startswith('below ')
        query_set = query_set.filter(rating__lte=float(rated_constraint[7:]))
      done = False

  # Last minute adjustments
  if query.startswith('gimme '):
    query = query[6:]
  elif query.startswith('give me '):
    query = query[8:]

  # Check for Genre queries
  genre_regex = re.compile('^an? ((?:\w|-)+)(?: movie| film)?$')
  match = genre_regex.search(query)
  if match:
    genre_name = match.group(1)
    genre = Genre.objects.get(name=genre_name)
    query_set = query_set.filter(movie_genres=genre)
  else:
    query_set = query_set.filter(name__icontains=query)
  return query_set
