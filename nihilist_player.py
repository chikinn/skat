"""A skat player that bids only for null games.

Nihilist only bids when she thinks she can win a null hand.  She skips the
kitty when her hand is strong and only reveals when victory is certain.

When not calling, she plays randomly like Kenny.  (What's the point...?)
"""

from skat_classes import *
from bot_utils import *

class NihilistPlayer:
    def __init__(self, seat):
        self.seat = seat

    def assess_hand(self, r):
        """Assess null hand strength to determine how high to bid."""
        self.hand = r.h[self.seat]
        self.hand.reorganize('null')

        nVulnerabilities = 0

        safeTricks = 0
        for suit in self.hand.cards[:-1]: # Skip empty trump suit.
            safeTricks += count_certain_tricks(suit, True)
        print(safeTricks)
        self.hand.show(r.zazz[1])

        if safeTricks < 8:
            self.maxBid = 0
        elif safeTricks == 8:
            self.maxBid = 23 # Vanilla null game
        elif safeTricks == 9:
            self.maxBid = 35 # Skip kitty (or reveal)
        elif safeTricks == 10:
            self.maxBid = 59 # Skip and reveal

    def bid(self, _, r):
        return bid_incrementally(r, self.maxBid)

    def kitty(self, _, __):
        return True # Always take the kitty.

    def discard(self, h, _):
        return get_random(h, 2)
 
    def declare(self, _, r):
        return ['null']

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
