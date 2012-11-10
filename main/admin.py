from django.contrib import admin
from gimme.main.models import Movie, Genre, Person, Seen

admin.site.register(Movie)
admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(Seen)
