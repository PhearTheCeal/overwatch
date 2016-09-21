""" Tool for finding counter data for heroes """
import urllib2
import base64
import os
from bs4 import BeautifulSoup

HOST = 'http://www.owfire.com'


def get_soup(url):
    """ Retreieve data from cache, or fetch and cache if missing """
    cache_name = base64.b64encode(bytes([hash(url)]))
    if os.path.isfile(cache_name):
        with open(cache_name) as cache:
            soup = BeautifulSoup(cache.read(), 'html.parser')
    else:
        req = urllib2.Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (X11; Linux i686; rv:10.0)'
                       + 'Gecko/20100101 Firefox/10.0')
        resp = urllib2.urlopen(req)
        html_doc = resp.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        with open(cache_name, 'w') as cache:
            cache.write(soup.prettify().encode('utf8'))

    return soup


def get_counters():
    """ Return dict of heroes and how well they counter other heroes """
    index_soup = get_soup(HOST + '/overwatch/counters')
    counters = {}

    for link in index_soup.select('.heroes a'):
        soup = get_soup(HOST + link.get('href'))
        hero_name = link.get('href').split('/')[-2]
        counters[hero_name] = {hero_name: 0.5}
        for desc in soup.select('.counters')[0].select('.desc'):
            counter_hero = desc.select('.comments')[0].get('href').split('/')[-1]
            up_votes = float(desc.select('.up')[0].text.strip())
            down_votes = float(desc.select('.down')[0].text.strip())
            counters[hero_name][counter_hero] = up_votes / (up_votes + down_votes)
    for hero in counters:
        for counter in counters[hero]:
            winrate1 = counters[hero][counter]
            winrate2 = 1.0 - counters[counter][hero]
            counters[hero][counter] = (winrate1 + winrate2) / 2.0
            counters[counter][hero] = 1 - ((winrate1 + winrate2) / 2.0)
    return counters


def main():
    """ print hero counters """
    counters = get_counters()
    for hero in counters:
        print hero
        for enemy, winrate in sorted(counters[hero].items(), key=lambda n: n[1]):
            print '\t', enemy, winrate


if __name__ == "__main__":
    main()
