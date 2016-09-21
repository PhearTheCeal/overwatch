""" Overwatch team finding tool. """

import itertools
import argparse
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

JACOB = ['reaper', 'mccree', 'roadhog', 'dva', 'junkrat', 'reinhardt', 'bastion', 'zenyatta', 'lucio']
KEVIN = ['bastion', 'soldier-76', 'reinhardt', 'mei', 'zenyatta', 'winston', 'zarya']
DAVID = ['dva', 'roadhog', 'mercy', 'mccree', 'tracer']  # , 'soldier-76', 'lucio', 'pharah', 'ana']
CRITTER = ['zenyatta', 'pharah', 'reinhardt', 'bastion', 'torbjorn']


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
    if args.jacob:
        player_choices.append(JACOB)
    if args.kevin:
        player_choices.append(KEVIN)
    if args.david:
        player_choices.append(DAVID)
    if args.critter:
        player_choices.append(CRITTER)
    for random_hero in args.random:
        player_choices.append([random_hero])

    possible_teams = sort_by_weakest_link(set(s)
                                          for s in
                                          itertools.product(*player_choices)
                                          if len(set(s)) == len(s))
    possible_teams = list(k for k, _ in itertools.groupby(possible_teams))

    for team in possible_teams:
        team_set = set(team)
        if any(len(team_set.intersection(role)) < 1 for role in (TANKS, HEALERS)):
            continue
        weak = weakest_link(team)
        print "{} --- WEAKEST LINK {} against {} {} --- POWER LEVEL {}".format(
                ' '.join(sorted(team)), weak['hero'], weak['counter'], weak['winrate'], sum_rank(team))


if __name__ == '__main__':
    main()
