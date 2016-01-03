#!/usr/local/bin/python

from skat_classes import *
from kenny_player import KennyPlayer

def play_one_round(p0, p1, p2):
    # Setup
    p = (p0, p1, p2) # Players
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
            declarer = advancer
            break
        if not r.get_bid(p[advancer], advancer):
            declarer = 2
            break

    if r.bidHistory == [False, False]: # First players both passed.
        if not r.get_bid(p[0], 0):
            return scores # All players score no points.
        else:
            declarer = 0
    
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
    print(r.playHistory)
    return scores

scores = play_one_round(KennyPlayer(), KennyPlayer(), KennyPlayer())
print(scores)
