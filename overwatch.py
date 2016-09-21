""" Overwatch team finding tool. """

import itertools
import argparse
from collections import Counter
from random import shuffle
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

KOK = {
    "Jacob": set(['reaper', 'mccree', 'roadhog', 'dva', 'junkrat', 'reinhardt', 'bastion', 'zenyatta', 'lucio']),
    "Kevin": set(['bastion', 'soldier-76', 'reinhardt', 'mei', 'zenyatta', 'winston', 'zarya']),
    "David": set(['dva', 'roadhog', 'mercy', 'mccree', 'tracer', 'soldier-76', 'lucio']),
    "Critter": set(['zenyatta', 'pharah', 'reinhardt', 'bastion', 'torbjorn'])
}


def main():
    """ Find team based on two randoms """
    parser = argparse.ArgumentParser()
    parser.add_argument('random', nargs='+')
    parser.add_argument('--mastery', action='store_true')

    parser.add_argument('--jacob', dest='players', action='append_const', const='Jacob')
    parser.add_argument('--kevin', dest='players', action='append_const', const='Kevin')
    parser.add_argument('--david', dest='players', action='append_const', const='David')
    parser.add_argument('--critter', dest='players', action='append_const', const='Critter')
    args = parser.parse_args()

    if args.mastery:
        for player in KOK:
            KOK[player] = set(COUNTERS.keys())

    player_choices = []
    pick_pool = {}
    for player in args.players:
        player_choices.append(KOK[player])
        pick_pool[player] = Counter()
    for random_hero in args.random:
        player_choices.append([random_hero])

    possible_teams = sort_by_weakest_link(set(s)
                                          for s in
                                          itertools.product(*player_choices)
                                          if len(set(s)) == len(s))
    possible_teams = list(k for k, _ in itertools.groupby(possible_teams))

    printed_top_team = False
    thresh = None
    for team in possible_teams:
        if any(len(team.intersection(role)) < 1 for role in (TANKS, HEALERS)):
            continue

        weak = weakest_link(team)
        if thresh is None:
            thresh = weak['winrate']
        if weak['winrate'] < thresh:
            break

        if not printed_top_team:
            print " ".join(team), weak['winrate']
            printed_top_team = True

        for player in args.players:
            pick_pool[player] += Counter((team - set(args.random) & KOK[player]))

    shuffle(args.players)
    for player in args.players:
        print player
        for hero in sorted(pick_pool[player],
                           reverse=True,
                           key=lambda n: pick_pool[player][n]):
            print '\t', hero, pick_pool[player][hero]


if __name__ == '__main__':
    main()
