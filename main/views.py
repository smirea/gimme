from django.http import HttpResponse


def example(request):
  if "name" in request.GET:
    name = " " + request.GET['name']
  else:
    name = ""
  return HttpResponse(
      "Hello%s, you will be baked, and then there will be cake" % name)
