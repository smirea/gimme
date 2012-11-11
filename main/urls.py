from django.conf.urls import patterns, include, url

import gimme.main.views as views

urlpatterns = patterns('',
  url(r'^$', views.example, name='example'),
  url(r'^api/query$', views.query, name='query'),
  url(r'^api/login$', views.login_view, name='login'),
  url(r'^api/logout$', views.logout_view, name='login'),
)
