import json
import statistics
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
    return render(request, "team_builder.html", {'heroes': sorted(overwatch.COUNTERS.keys())})

def team_builder_res(request):
    players = json.loads(request.POST.get('player_json'), {})
    randoms = request.POST.getlist('random')
    teams, top = overwatch.find_teams(players, randoms, False, not request.POST.get('meta'))
    teams = {k: sorted(v.items(), reverse=True, key=lambda x: (x[1], [0])) for k, v in teams.items()}
    return render(request, 'team_builder_res.html', {'teams': teams, 'top_teams': top})

def counters(request, hero=None):
    if hero in overwatch.COUNTERS.keys():
        counters = dict(overwatch.COUNTERS[hero])
        counters = {k: overwatch.pretty_percent(v) for k, v in counters.items()}
        counter_items = sorted(counters.items(), key=lambda n: float(n[1]))
        rates = [float(n[1]) for n in counters.items()]
        avg_win = overwatch.pretty_percent(sum(rates) / len(rates) / 100.0)
        min_win = min(rates)
        max_win = max(rates)
        sd_win = overwatch.pretty_percent(statistics.stdev(rates) / 100.0)
        pagerank = overwatch.pretty_percent(overwatch.RANKINGS[hero])
        return render(request,
                      'hero_counters.html',
                      {'hero': hero,
                       'counter_items': counter_items,
                       'pagerank': pagerank,
                       'min_winrate': min_win,
                       'avg_winrate': avg_win,
                       'max_winrate': max_win,
                       'sd_winrate': sd_win})
    elif hero:
        return HttpResponse("{} isn't a hero".format(hero))
    else:
        return render(request, 'counters.html', {'hero_list': sorted(overwatch.COUNTERS.keys())})
