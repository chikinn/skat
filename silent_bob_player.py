"""A random skat player that never bids.

Silent Bob is a minor modification of Kenny (kenny_player).  He plays randomly,
like Kenny, but never bids.

See play_skat and the Round class in skat_classes for context.
"""

from skat_classes import *

class SilentBobPlayer:
    def bid(self, h, r):
        return False

    def kitty(self, h, r):   #
        pass                 # These methods will never be called because
                             # it's impossible for Bob to win the bidding.
    def discard(self, h, r): #
        pass                 #
                             #
    def declare(self, h, r): #
        pass                 #

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
