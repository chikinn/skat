#!/usr/local/bin/python
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

PERMUTATIONS = ((0,1,2), (0,2,1), (1,0,2), (1,2,0), (2,0,1), (2,1,0))

def usage():
    """Print a standard Unix usage string."""
    print('usage: {} player1 player2 player3 n_rounds verbosity'
          .format(sys.argv[0]))
    print('  playeri: kenny or bob')
    print('  n_rounds: positive integer (preferably a multiple of 6)')
    print('  verbosity: silent, scores, or verbose')
    sys.exit(2)


if len(sys.argv) != 6:
    usage()

# Load players.
names = sys.argv[1:4]
players = []
for i in range(3):
    if names[i] == 'kenny':
        players.append(KennyPlayer())
    elif names[i] == 'bob':
        players.append(SilentBobPlayer())
    names[i] = names[i].capitalize()

# Resolve duplicate names by appending '1', '2', and '3' as needed.
if names[0] == names[1] == names[2]:
    names = [names[i] + str(i + 1) for i in range(3)]
else:
    for pair in ((0,1), (0,2), (1,2)):
        if names[pair[0]] == names[pair[1]]:
            names[pair[0]] += '1'
            names[pair[1]] += '2'

# Pad names for better verbose display.
longestName = ''
for name in names:
    if len(name) > len(longestName):
        longestName = name
for name in names:
    while len(name) < len(longestName):
        name += ' '

# Ideally, to sample permutations evenly, this should be a multiple of 3! = 6.
nRounds = int(sys.argv[4])

verbosity = sys.argv[5]

# Play rounds.
scores = [[], [], []]
for i in range(nRounds):
    if verbosity == 'verbose':
        print('\n' + 'ROUND {}:'.format(i))
    permutation = PERMUTATIONS[i % 6]
    score = play_one_round([players[p] for p in permutation],
                           [names[p] for p in permutation],
                           verbosity)
    for j, p in enumerate(permutation):
        scores[p].append(score[j])

# Print average scores.
if verbosity != 'silent':
    print('')
print('AVERAGE SCORES (+/- 1 std. err.):')
for i in range(3):
    print('{}, {} +/- {}'.format(names[i],
                                 str(mean(scores[i]))[:5],
                                 str(stats.sem(scores[i]))[:4] ))
