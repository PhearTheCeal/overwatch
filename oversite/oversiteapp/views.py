from django.shortcuts import render
from django.http import HttpResponse

from .overwatch import find_teams

def index(request):
    return HttpResponse("Hello world!")

def team_builder(request):
    return HttpResponse("GET = {}".format(dict(request.GET)))

def counters(request):
    return HttpResponse("This will be an index of heroes. Clicking takes you to counter/hero and shows counters.")
