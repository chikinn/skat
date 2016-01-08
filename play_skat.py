from skat_classes import *

def play_one_round(players, names, verbosity):
    # Setup
    r = Round(names, verbosity) # Instantiation of a single round of Skat
    r.generate_deck()
    scores = [0, 0, 0]
    
    # Bidding
    while True: # Repeat until a player passes.
        if not r.get_bid(players[1], 1):
            advancer = 0
            break
        if not r.get_bid(players[0], 0):
            advancer = 1
            break
    
    while True:
        if not r.get_bid(players[2], 2):
            declarer = advancer
            break
        if not r.get_bid(players[advancer], advancer):
            declarer = 2
            break

    if r.bidHistory == [False, False]: # First players both passed.
        if not r.get_bid(players[0], 0):
            if verbosity == 'scores':
                print('everyone passed')
            return scores # All players score no points.
        else:
            declarer = 0
    
    # Declaring (first kitty, then game type and other extras)
    if r.get_kitty_declaration(players[declarer], declarer):
        r.give_kitty()
        r.get_kitty_discards(players[declarer])
    r.get_declaration(players[declarer])
    
    overbid = r.check_overbid()
    if overbid:
        scores[declarer] = -2 * overbid
        return scores
    
    # Trick taking
    for _ in range(N_CARDS):
        r.get_play(players[r.whoseTurn])
        r.next_turn()
    
    # Scoring
    scores[declarer] = r.score()
    return scores
