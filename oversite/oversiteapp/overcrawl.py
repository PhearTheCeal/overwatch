""" Tool for finding counter data for heroes """
import urllib.request
import os
import json
import sys
from multiprocessing import Pool
from bs4 import BeautifulSoup

HOST = 'http://www.owfire.com'


def get_soup(url):
    """ Request url, parse into soup, return """
    req = urllib.request.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (X11; Linux i686; rv:10.0)'
                   + 'Gecko/20100101 Firefox/10.0')
    resp = urllib.request.urlopen(req)
    html_doc = resp.read()
    return BeautifulSoup(html_doc, 'html.parser')


def get_hero_data(url):
    """ Get hero counter data based on url """
    soup = get_soup(url)
    hero_name = url.split('/')[-2]

    hero_data = []
    for desc in soup.select('.counters')[0].select('.desc'):
        counter_hero = desc.select('.comments')[0].get('href').split('/')[-1]
        up_votes = float(desc.select('.up')[0].text.strip())
        down_votes = float(desc.select('.down')[0].text.strip())
        hero_data.append({'up': up_votes, 'down': down_votes, 'counter_hero': counter_hero})

    return {hero_name: hero_data}


def get_counters():
    """ Return dict of heroes and how well they counter other heroes """
    if os.path.isfile('.counter_cache'):
        with open('.counter_cache') as cache:
            return json.load(cache)
    counters = {}

    index_soup = get_soup(HOST + '/overwatch/counters')
    pool = Pool()
    hero_data = pool.map(get_hero_data, (HOST + link.get('href')
                                         for link in index_soup.select('.heroes a')))

    for hero in hero_data:
        hero_name = list(hero.keys())[0]
        counters[hero_name] = {hero_name: 0.5}
        for counter in list(hero.values())[0]:
            counter_hero = counter['counter_hero']
            up_votes = counter['up']
            down_votes = counter['down']
            counters[hero_name][counter_hero] = up_votes / (up_votes + down_votes)

    for hero in counters:
        for counter in counters[hero]:
            winrate1 = counters[hero][counter]
            winrate2 = 1.0 - counters[counter][hero]
            counters[hero][counter] = (winrate1 + winrate2) / 2.0
            counters[counter][hero] = 1 - ((winrate1 + winrate2) / 2.0)

    with open('.counter_cache', 'w') as cache:
        json.dump(counters, cache)
    return counters


def main():
    """ print hero counters """
    counters = get_counters()
    requested = counters if len(sys.argv) < 2 else sys.argv[1:]
    for hero in requested:
        print(hero)
        for enemy, winrate in sorted(counters[hero].items(), key=lambda n: n[1]):
            print('\t', enemy, winrate)


if __name__ == "__main__":
    main()
