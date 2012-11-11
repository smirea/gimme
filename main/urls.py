from django.conf.urls import patterns, include, url

import gimme.main.views as views

urlpatterns = patterns('',
  url(r'^$', views.index, name='index'),
  url(r'^api/test$', views.test, name='test'),
  url(r'^api/cinema$', views.cinema, name='cinema'),
  url(r'^api/query$', views.query, name='query'),
  url(r'^api/friend_list$', views.friend_list, name='friend_list'),
  url(r'^api/login$', views.login_view, name='login'),
  url(r'^api/logout$', views.logout_view, name='logout'),
)
