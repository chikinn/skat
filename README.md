# Skat
#### By Robert B. Kaspar and Jake Kaspar

## Usage
    usage: ./skat_wrapper.py player1 player2 player3 n_rounds verbosity
      playeri: kenny or bob
      n_rounds: positive integer (preferably a multiple of 6)
      verbosity: silent, scores, or verbose

## Example usage
    $ ./skat_wrapper.py kenny kenny bob 6 verbose

## Example output
    ROUND 2:
    [BIDS]   Kenny1 bids 18
             Kenny2 bids True
             Kenny1 bids False
             Bob    bids False
    Kenny2 calls grand
    [HANDS]  Kenny2: 7d 8d kd | 7s ks | 8h qh | 8c qc kc | 
             Kenny1: td ad | 8s 9s as | ah | 7c ac | js jc
             Bob   : 9d qd | qs ts | 7h 9h kh th |  | jd jh
    [TRICKS] Kenny2 leads qh ah th --> Kenny1
             Kenny1 leads as qs ks --> Kenny1
             Kenny1 leads td qd kd --> Kenny1
             Kenny1 leads 7c jh 8c --> Bob   
             Bob    leads kh 8h js --> Kenny1
             Kenny1 leads ac 9h kc --> Kenny1
             Kenny1 leads 8s ts 7s --> Bob   
             Bob    leads jd qc jc --> Kenny1
             Kenny1 leads 9s 7h 7d --> Kenny1
             Kenny1 leads ad 9d 8d --> Kenny1
    loses three quarters, loses everything!
    Kenny2 scores -336

I guess Kenny's game could use a little work!

## Analysis of KennyPlayer
Random play in such a complex game is punishing: in a match between three
KennyPlayers, the average score is quite negative.  The declarer loses most
hands.

Interestingly, the Kenny in the middle seat scores 30% higher (well, less
negative) on average.  This is because the middle seat bids first, and Kenny's
best "strategy" in the bidding is not to bid at all (since a Kenny declarer
usually loses).  With the advantage of bidding first, even if Kenny doesn't
pass immediately, there's a good chance one of the other players will bid,
giving him another chance to pass.

Similarly, when one or more Kennys are replaced by SilentBob, who is identical
to Kenny except that he refuses to bid, Kenny fares even worse: he has fewer
other bidders to rely on to save him from his own disastrous bidding.  Here are
Kenny's average scores (100,000 games) as a function of the number of Bobs:

    3 Kennys / 0 Bobs, -20.4 +/- 0.15
    2 Kennys / 1 Bob,  -26.1 +/- 0.16
    1 Kenny  / 2 Bobs, -34.3 +/- 0.18
