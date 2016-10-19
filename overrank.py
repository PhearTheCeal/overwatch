""" Tool for finding the PageRank of heroes """
import numpy as np
from scipy.sparse import csc_matrix
from overcrawl import get_counters

COUNTERS = get_counters()
ALL_HEROES = list(COUNTERS.keys())

MATRIX = [[COUNTERS[c].get(h, 0) for c in ALL_HEROES] for h in ALL_HEROES]


def page_rank(G, s=0.85, maxerr=0.0000000000001):
    """
    Computes the pagerank for each of the n states.
    Used in webpage ranking and text summarization using unweighted
    or weighted transitions respectively.
    Args
    ----------
    G: matrix representing state transitions
       Gij can be a boolean or non negative real number representing the
       transition weight from state i to j.
    Kwargs
    ----------
    s: probability of following a transition. 1-s probability of teleporting
       to another state. Defaults to 0.85
    maxerr: if the sum of pageranks between iterations is bellow this we will
            have converged. Defaults to 0.001
    """
    # pylint: disable=invalid-name, too-many-locals
    n = G.shape[0]

    # transform G into markov matrix M
    M = csc_matrix(G, dtype=np.float)
    rsums = np.array(M.sum(1))[:, 0]
    ri, _ = M.nonzero()
    M.data /= rsums[ri]

    # bool array of sink states
    sink = rsums == 0

    # Compute pagerank r until we converge
    ro, r = np.zeros(n), np.ones(n)
    while True:
        ro = r.copy()
        # calculate each pagerank at a time
        for i in range(0, n):
            # inlinks of state i
            Ii = np.array(M[:, i].todense())[:, 0]
            # account for sink states
            Si = sink / float(n)
            # account for teleportation to state i
            Ti = np.ones(n) / float(n)

            r[i] = ro.dot(Ii*s + Si*s + Ti*(1-s))
        r_norm = r / sum(r)
        ro_norm = ro / sum(ro)
        if np.sum(np.abs(r_norm - ro_norm)) <= maxerr:
            break

    # return normalized pagerank
    return r/sum(r)


def get_rankings():
    """ Get ranking for each hero in order """
    graph = np.array(MATRIX)
    res = page_rank(graph)
    res = list(res)
    return dict(zip(ALL_HEROES, res))


def main():
    """ Main function """
    ranks = get_rankings()
    heroes = sorted(ALL_HEROES, key=lambda n: ranks[n])[::-1]

    for hero in heroes:
        print("{:16s} {}".format(hero, int(1000*ranks[hero])))

if __name__ == '__main__':
    main()
