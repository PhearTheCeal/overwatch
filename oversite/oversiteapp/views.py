import json
from django.shortcuts import render
from django.http import HttpResponse

from . import overwatch

def index(request):
    return render(request, 'index.html', {})

def preferences(request):
    return render(request,
                  'preferences.html',
                  {'hero_list': sorted(overwatch.COUNTERS.keys())})

def team_builder(request):
    if request.method == 'GET':
        return render(request, "team_builder.html")
    elif request.method == 'POST':
        players = json.loads(request.POST.get('player_json'), {})
        teams = overwatch.find_teams(players, [], True, True)
        teams = {k: dict(v) for k, v in teams.items()}
        return render(request, 'team_builder.html', {'teams': teams})

def counters(request, hero=None):
    if hero in overwatch.COUNTERS.keys():
        counters = dict(overwatch.COUNTERS[hero])
        counters = {k: "{0:.1f}".format(round(100*v, 1)) for k, v in counters.items()}
        counter_items = sorted(counters.items(), key=lambda n: float(n[1]))
        return render(request,
                      'hero_counters.html',
                      {'hero': hero, 'counter_items': counter_items})
    elif hero:
        return HttpResponse("{} isn't a hero".format(hero))
    else:
        return render(request, 'counters.html', {'hero_list': overwatch.COUNTERS.keys()})
