from django.conf.urls import patterns, include, url

import gimme.main.views as views

urlpatterns = patterns('',
  url(r'^$', views.example, name='example'),
  url(r'^api/query$', views.query, name='query'),
)
