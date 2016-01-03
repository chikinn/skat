#!/usr/local/bin/python

from skat_classes import *
from kenny_player import KennyPlayer

# Setup
p = (KennyPlayer(), KennyPlayer(), KennyPlayer()) # Players 0, 1, and 2
r = Round() # Instantiation of a single round of Skat
r.generate_deck()
scores = [0, 0, 0]

# Bidding
while True: # Repeat until a player passes.
    if not r.get_bid(p[1], 1):
        advancer = 0
        break
    if not r.get_bid(p[0], 0):
        advancer = 1
        break

while True:
    if not r.get_bid(p[2], 2):
        if r.currentBid >= MIN_BID: # Check that at least someone bid.
            declarer = advancer
            break
    if not r.get_bid(p[advancer], advancer):
        if r.currentBid >= MIN_BID:
            declarer = 2
            break
        else: # No one bid.  Redeal.
            return scores # All players score no points.

# Declaring (first kitty, then game type and other extras)
if r.get_kitty_declaration(p[declarer], declarer):
    r.give_kitty()
    r.get_kitty_discards(p[declarer])
r.get_declaration(p[declarer])

overbid = r.check_overbid()
if overbid:
    scores[declarer] = -2 * overbid
    return scores

# Trick taking
for _ in range(N_CARDS):
    r.get_play(p[r.whoseTurn])
    r.next_turn()

# Scoring
scores[declarer] = r.score()
return scores
