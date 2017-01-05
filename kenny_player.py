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
    def get_random(self, h):
        if type(h.cards[0]) == list:
            flat = sum(h.cards, [])
        else:
            flat = h.cards
        return random.choice(flat)

    def initialize_bidding(self):
        bidIndex = -1
        while bool(random.getrandbits(1)): # Coin flip
            bidIndex += 1
        if bidIndex == -1:
            self.maxBid = LEGAL_BIDS[0] - 1 # Pass immediately.
        else:
            self.maxBid = LEGAL_BIDS[bidIndex]

    def bid(self, _,  r):
        self.initialize_bidding()
        return bid_incrementally(r, self.maxBid)

    def kitty(self, h, r):
        return True

    def discard(self, h, r):
        kitty1 = 0
        kitty2 = 0
        while kitty1 == kitty2:
            kitty1 = self.get_random(h)
            kitty2 = self.get_random(h)
        return [kitty1,kitty2]
 
    def declare(self, h, r):
        if r.currentBid > 23: # Forbid an illegal overbid null game.
            return [random.choice([g for g in GAMES if g != 'null'])]
        return [random.choice(GAMES)]

    def play(self, h, r):
        return random.choice(r.legal_plays(h))
