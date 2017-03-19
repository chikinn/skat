#!/usr/bin/env python
"""Wrapper for playing more than one round of skat.

Command-line arguments (see usage):
  playeri: Name of the AI that will control each player
  nRounds: Number of rounds to play
  verbosity: How much output to show ('silent', only final average scores;
    'scores', result of each round; 'verbose', play by play)
"""

import sys
from scipy import stats, mean
from play_skat import play_one_round
from kenny_player import KennyPlayer
from silent_bob_player import SilentBobPlayer
from nihilist_player import NihilistPlayer

N_PLAYERS    = 3
PERMUTATIONS = ((0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0))

def usage():
    """Print a standard Unix usage string."""
    print('usage: {} player1 player2 player3 n_rounds verbosity'
          .format(sys.argv[0]))
    print('  playeri: kenny or bob')
    print('  n_rounds: positive integer (preferably a multiple of 6)')
    print('  verbosity: silent, scores, or verbose')
    sys.exit(2)

def make_player(name, seat):
    """Instantiate and return a player."""
    if name == 'kenny':
        return KennyPlayer(seat)
    elif name == 'bob':
        return SilentBobPlayer(seat)
    elif name == 'nihilist':
        return NihilistPlayer(seat)

if len(sys.argv) != 6:
    usage()

names = sys.argv[1 : 1 + N_PLAYERS]

# Capitalize player names.
prettyNames = []
for i in range(N_PLAYERS):
    prettyNames.append(names[i].capitalize())

# Resolve duplicate names by appending '1', '2', and '3' as needed.
if names[0] == names[1] == names[2]:
    prettyNames = [prettyNames[i] + str(i + 1) for i in range(N_PLAYERS)]
else:
    for pair in ((0,1), (0,2), (1,2)):
        if names[pair[0]] == names[pair[1]]:
            prettyNames[pair[0]] += '1'
            prettyNames[pair[1]] += '2'

# Pad names for better verbose display.
longestName = ''
for name in prettyNames:
    if len(name) > len(longestName):
        longestName = name
for i in range(N_PLAYERS):
    while len(prettyNames[i]) < len(longestName):
        prettyNames[i] += ' '

# Ideally, to sample permutations evenly, should be a multiple of 3! = 6.
nRounds = int(sys.argv[4])

verbosity = sys.argv[5]

# Play rounds.
scores = [[], [], []]
for i in range(nRounds):
    if verbosity == 'verbose':
        print('\n' + 'ROUND {}:'.format(i))
    permutation = PERMUTATIONS[i % 6]
    ### TODO: necessary to re-instantiate players every round?
    score = play_one_round([make_player(names[p], j) \
                               for j, p in enumerate(permutation)],
                           [prettyNames[p] for p in permutation],
                           verbosity)
    for j, p in enumerate(permutation):
        scores[p].append(score[j])

# Print average scores.
if verbosity != 'silent':
    print('')
print('AVERAGE SCORES (+/- 1 std. err.):')
for i in range(N_PLAYERS):
    # stat.sem() throws a warning if nRounds is small.  No big deal.
    print('{}, {} +/- {}'.format(prettyNames[i],
                                 str(mean(scores[i]))[:5],
                                 str(stats.sem(scores[i]))[:4] ))
