from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^counters/(?P<hero>[-\w]*)', views.counters, name='counters'),
    url(r'team_builder/', views.team_builder, name='team_builder')
]
