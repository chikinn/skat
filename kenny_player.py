"""A random skat player.

Kenny always chooses a random card to play.  In the bidding, half the time he
passes and half the time he makes the (lowest) next legal bid.  When declaring,
he picks a game uniformly at random (and thus is biased toward suit games,
of which there are four compared to just one null option and one grand option),
always takes the kitty, and never calls any extras.

See play_skat and the Round class in skat_classes for context.
"""

from skat_classes import *
from bot_utils import *

class KennyPlayer:
    def __init__(self):
        """Flip coins to determine how high to bid."""
        bidIndex = -1
        while bool(random.getrandbits(1)): # Coin flip
            bidIndex += 1
        if bidIndex == -1:
            self.maxBid = LEGAL_BIDS[0] - 1 # Pass immediately.
        else:
            self.maxBid = LEGAL_BIDS[bidIndex]

    def bid(self, _,  r):
        return bid_incrementally(r, self.maxBid)

    def kitty(self, _, __):
        return True # Always take the kitty.

    def discard(self, h, _):
        return get_random(h, 2)
 
    def declare(self, _, r):
        if r.currentBid > 23: # Forbid an illegal overbid null game.
            return [random.choice([g for g in GAMES if g != 'null'])]
        return [random.choice(GAMES)]

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
