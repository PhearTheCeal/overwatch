""" Overwatch team finding tool. """

import itertools
from collections import Counter
from .overcrawl import get_counters
from .overrank import get_rankings


def weakest_link(team):
    """
    Returns dict {'winrate': weakest_winrate, 'hero': link, 'counter': link_breaker}
    for the given team.
    """
    weakest_winrate = float('inf')
    link = None
    link_breaker = None
    for counter in COUNTERS:
        max_winrate = 0.0
        max_hero = None
        for hero in team:
            if COUNTERS[hero][counter] > max_winrate:
                max_winrate = COUNTERS[hero][counter]
                max_hero = hero
        if max_winrate < weakest_winrate:
            weakest_winrate = max_winrate
            link = max_hero
            link_breaker = counter
    return {'winrate': weakest_winrate, 'hero': link, 'counter': link_breaker}


def team_pagerank(team):
    return sum(RANKINGS[hero] for hero in team)

def sort_by_weakest_link(teams):
    """ Sort by weakest link then by power level """
    return sorted(teams, reverse=True, key=lambda t: (weakest_link(t)['winrate'], team_pagerank(t)))

def pretty_percent(number):
    return "{0:.1f}".format(round(100*number, 1))

RANKINGS = get_rankings()
COUNTERS = get_counters()
TANKS = set(['dva', 'reinhardt', 'roadhog', 'winston', 'zarya'])
OFFENSE = set(['genji', 'pharah', 'reaper', 'mccree', 'soldier-76', 'tracer', 'sombra'])
DEFENSE = set(['bastion', 'hanzo', 'junkrat', 'mei', 'torbjorn', 'widowmaker'])
SUPPORT = set(['lucio', 'symmetra', 'mercy', 'ana', 'zenyatta'])
HEALERS = SUPPORT.difference(set(['symmetra']))
DPS = OFFENSE.union(DEFENSE)


def find_teams(players=None, randoms=None, inclusive=False, no_meta=False):
    """ Find team based on two randoms """
    players = players or {}
    randoms = randoms or []

    player_choices = []
    pick_pool = {}
    for player in players:
        player_choices.append(set(players[player]))
        pick_pool[player] = Counter()
    for random_hero in randoms:
        player_choices.append(set([random_hero]))

    team_size = len(randoms) + len(players)
    hero_pool = set()
    for choice in player_choices:
        hero_pool |= choice

    possible_teams = [set(t) for t in itertools.combinations(hero_pool, team_size)]
    possible_teams = [t for t in possible_teams if all(x & t for x in player_choices)]
    possible_teams = sort_by_weakest_link(possible_teams)
    if not no_meta:
        possible_teams = [team for team in possible_teams
                          if all(len(team.intersection(role)) == 2 for role in (TANKS, SUPPORT, DPS))]

    thresh = 0.5000000000001 if inclusive else None
    for team in possible_teams:
        weak = weakest_link(team)
        if thresh is None:
            thresh = weak['winrate']
        if weak['winrate'] < thresh:
            break

        for player in players:
            pick_pool[player] += Counter((team - set(randoms) & set(players[player])))

    return pick_pool, [(", ".join(sorted(list(team))), pretty_percent(weakest_link(team)['winrate']), pretty_percent(team_pagerank(team))) for team in possible_teams[:5]]
