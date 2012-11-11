# Natural Language Processing for the win.

import re

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
  if len(tags):
    if query.endswith(' include'):
      query = query[:-8].strip()
    elif query.endswith(' with'):
      query = query[:-5].strip()

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
    matches = re.match('the (\d{3})\ds', year)
    if matches:
      group = int(matches.group(1)) * 10
      return group, group + 9
    matches = re.match('the (\d)\ds', year)
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

  rated_regex = re.compile("(rated below \d(\.\d)?|rated above \d(\.\d)?)$")

  # name_fragment = "\w+\W+\w+"
  # with_actor_regex = re.compile("starring " + name_fragment)
  # with_director_regex = re.compile("directed by " + name_fragment)

  done = False
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

  query_set = query_set.filter(name__icontains=query)
  return query_set
