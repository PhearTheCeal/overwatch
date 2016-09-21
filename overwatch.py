""" Overwatch team finding tool. """
# pylint: disable=too-many-branches,too-many-statements

import itertools
import argparse
from collections import Counter
from overcrawl import get_counters
from overrank import get_rankings

COUNTERS = get_counters()
RANK = get_rankings()


def sum_rank(team):
    """ Team power level """
    return sum(RANK[h] for h in team)


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


def sort_by_weakest_link(teams):
    """ Sort by weakest link then by power level """
    return sorted(teams, reverse=True, key=lambda t: (weakest_link(t)['winrate'], sum_rank(t)))

TANKS = set(['dva', 'reinhardt', 'roadhog', 'winston', 'zarya'])
OFFENSE = set(['genji', 'pharah', 'reaper', 'mccree', 'soldier-76', 'tracer'])
DEFENSE = set(['bastion', 'hanzo', 'junkrat', 'mei', 'torbjorn', 'widowmaker'])
SUPPORT = set(['lucio', 'symmetra', 'mercy', 'ana', 'zenyatta'])
HEALERS = SUPPORT.difference(set(['symmetra']))
DPS = OFFENSE.union(DEFENSE)

JACOB = set(['reaper', 'mccree', 'roadhog', 'dva', 'junkrat', 'reinhardt', 'bastion', 'zenyatta', 'lucio'])
KEVIN = set(['bastion', 'soldier-76', 'reinhardt', 'mei', 'zenyatta', 'winston', 'zarya'])
DAVID = set(['dva', 'roadhog', 'mercy', 'mccree', 'tracer', 'soldier-76', 'lucio', 'pharah', 'ana'])
CRITTER = set(['zenyatta', 'pharah', 'reinhardt', 'bastion', 'torbjorn'])


def main():
    """ Find team based on two randoms """
    parser = argparse.ArgumentParser()
    parser.add_argument('random', nargs='+')

    parser.add_argument('--jacob', action='store_true')
    parser.add_argument('--kevin', action='store_true')
    parser.add_argument('--david', action='store_true')
    parser.add_argument('--critter', action='store_true')
    args = parser.parse_args()

    player_choices = []
    pick_pool = {}
    if args.jacob:
        player_choices.append(JACOB)
        pick_pool['jacob'] = Counter()
    if args.kevin:
        player_choices.append(KEVIN)
        pick_pool['kevin'] = Counter()
    if args.david:
        player_choices.append(DAVID)
        pick_pool['david'] = Counter()
    if args.critter:
        player_choices.append(CRITTER)
        pick_pool['critter'] = Counter()
    for random_hero in args.random:
        player_choices.append([random_hero])

    possible_teams = sort_by_weakest_link(set(s)
                                          for s in
                                          itertools.product(*player_choices)
                                          if len(set(s)) == len(s))
    possible_teams = list(k for k, _ in itertools.groupby(possible_teams))

    print " ".join(possible_teams[0])
    for team in possible_teams:
        if any(len(team.intersection(role)) < 1 for role in (TANKS, HEALERS)):
            continue
        weak = weakest_link(team)
        if weak['winrate'] <= 0.5:
            break
        if args.jacob:
            pick_pool['jacob'] += Counter(team & JACOB)
        if args.david:
            pick_pool['david'] += Counter(team & DAVID)
        if args.kevin:
            pick_pool['kevin'] += Counter(team & KEVIN)
        if args.critter:
            pick_pool['critter'] += Counter(team & CRITTER)
    if args.jacob:
        print 'Jacob'
        for hero in sorted(pick_pool['jacob'], reverse=True, key=lambda n: pick_pool['jacob'][n]):
            print '\t', hero, pick_pool['jacob'][hero]
    if args.kevin:
        print 'Kevin'
        for hero in sorted(pick_pool['kevin'], reverse=True, key=lambda n: pick_pool['kevin'][n]):
            print '\t', hero, pick_pool['kevin'][hero]
    if args.david:
        print 'David'
        for hero in sorted(pick_pool['david'], reverse=True, key=lambda n: pick_pool['david'][n]):
            print '\t', hero, pick_pool['david'][hero]
    if args.critter:
        print 'Critter'
        for hero in sorted(pick_pool['critter'], reverse=True, key=lambda n: pick_pool['critter'][n]):
            print '\t', hero, pick_pool['critter'][hero]


if __name__ == '__main__':
    main()
