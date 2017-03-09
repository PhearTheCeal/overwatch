""" Overwatch team finding tool. """

import itertools
import multiprocessing
import signal
from collections import Counter
from .overcrawl import get_counters
from .overrank import get_rankings


def weakest_link(team, enemies, binary=False, current_best=0):
    if binary:
        team = set(BIN_HEROES[h] for h in team)
    else:
        team = set(h for h in team)
        enemies = set(h for h in enemies)

    # BEGIN shitty algorithm that I need to optimize
    weakest_link = float('inf')
    for e in enemies:
        c = max(COUNTERS[h][e] for h in team)
        if c < current_best:
            return c
        if c < weakest_link:
            weakest_link = c
    return weakest_link


def team_pagerank(team):
    """ Sum page rank of team """
    return sum(RANKINGS[hero] for hero in team)


def sort_by_weakest_link(teams, enemies):
    """ Sort by weakest link then by power level """
    return sorted(teams, reverse=True, key=lambda t: (weakest_link(t, enemies), team_pagerank(t)))


def pretty_percent(number):
    """ Convert a decimal percentage to something pretty """
    return "{0:.1f}".format(round(100*number, 1))

RANKINGS = get_rankings()
COUNTERS = get_counters()
ALL_HEROES = sorted(COUNTERS.keys())
SORTED_COUNTER_LIST = []
for hero, counters in COUNTERS.items():
    for enemy, winrate in counters.items():
        SORTED_COUNTER_LIST.append(tuple([enemy, winrate, hero]))
SORTED_COUNTER_LIST.sort(key=lambda x: x[1], reverse=True)
TANKS = set(['dva', 'reinhardt', 'roadhog', 'winston', 'zarya'])
OFFENSE = set(['genji', 'pharah', 'reaper', 'mccree', 'soldier-76', 'tracer', 'sombra'])
DEFENSE = set(['bastion', 'hanzo', 'junkrat', 'mei', 'torbjorn', 'widowmaker'])
SUPPORT = set(['lucio', 'symmetra', 'mercy', 'ana', 'zenyatta'])
HEALERS = SUPPORT.difference(set(['symmetra']))
DPS = OFFENSE.union(DEFENSE)


def hero_to_binary(hero):
    """ hero -> binary """
    return 1 << ALL_HEROES.index(hero)


def binary_to_hero(binary):
    """ binary -> hero """
    index = -1
    while binary:
        binary >>= 1
        index += 1
    return ALL_HEROES[index]

# binary -> hero cache
BIN_HEROES = {hero_to_binary(h): h for h in ALL_HEROES}

TANKS_BIN = set(hero_to_binary(h) for h in TANKS)
DPS_BIN = set(hero_to_binary(h) for h in DPS)
SUPPORT_BIN = set(hero_to_binary(h) for h in SUPPORT)


def gen_possible_teams(args):
    """ gen possible teams """
    return _gen_possible_teams(*args)


class TimeoutError(Exception):
    pass


def _gen_possible_teams(hero, choices, enemies, no_meta):
    results = []
    top_score = 0.0
    enemies_set = set(BIN_HEROES[h] for h in enemies)
    timeout = 3

    def _sig_alarm(sig, tb):
        raise TimeoutError("timeout")
    signal.signal(signal.SIGALRM, _sig_alarm)
    try:
        signal.alarm(timeout)
        for team in itertools.product([hero], *choices):
            # 1. Ensure team has no dupes
            t = set(team)
            if len(t) != len(team):
                continue
            # 1.5 Ensure meta if enforced
            if not no_meta:
                if any(len(t & role) != 2 for role in (TANKS_BIN, DPS_BIN, SUPPORT_BIN)):
                    continue
            # 2. Score team
            score = weakest_link(team, enemies_set, binary=True, current_best=top_score)
            if score > top_score:
                top_score = score
            if score < top_score:
                continue
            results.append((team, score))

    except TimeoutError:
        pass

    signal.alarm(0)

    return results


def find_teams(players=None, randoms=None, inclusive=False, no_meta=False, enemies=None):
    """ Find team based on two randoms """
    players = players or {}
    randoms = randoms or ()
    enemies = enemies or COUNTERS.keys()
    enemies = [hero_to_binary(h) for h in enemies]

    player_choices = []
    pick_pool = {p: Counter() for p in players}
    for player in players:
        player_choices.append(sorted((hero_to_binary(h) for h in players[player]),
                                     reverse=True,
                                     key=lambda x: RANKINGS[BIN_HEROES[x]]))
    for random_hero in randoms:
        player_choices.append([hero_to_binary(random_hero)])

    player_choices.sort(key=len, reverse=True)
    pool = multiprocessing.Pool()
    try:
        possible_teams = set()
        pool_args = ((hero, player_choices[1:], enemies, no_meta) for hero in player_choices[0])
        top_score = 0
        for list_of_teams in pool.imap(gen_possible_teams, pool_args):
            if list_of_teams and list_of_teams[-1][1] > top_score:
                top_score = list_of_teams[-1][1]
            if list_of_teams and list_of_teams[-1][1] < top_score:
                continue
            possible_teams.update(list_of_teams)
    finally:
        pool.terminate()
    possible_teams = filter(lambda x: x[1] == top_score, possible_teams)
    possible_teams = [[BIN_HEROES[h] for h in team[0]] for team in possible_teams]
    enemies = [BIN_HEROES[h] for h in enemies]

    for team in possible_teams:
        for player in players:
            pick_pool[player] += Counter((set(team) - set(randoms) & set(players[player])))

    return pick_pool, [(", ".join(sorted(list(team))),
                        pretty_percent(weakest_link(team, enemies)),
                        pretty_percent(team_pagerank(team)))
                       for team in possible_teams[:5]]
