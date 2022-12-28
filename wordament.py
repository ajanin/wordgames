#!/usr/bin/env python3
#
# ./wordament.py pmrepea[en]rihbbslt
#
# TODO:
#
# Get a better word list.
# Figure out scoring for real.
# Do filtering (e.g. star rewards) here rather than on command line.
# Maybe add interactive loop so I can record what's conisdered a real word and track scoring?
#

import argparse
import logging
import re
import sys

from typing import Tuple, Dict, List

VERSION = 0.1


class Global:
    """Stores globals. There should be no instances of Global."""

    # Command line arguments
    args = None

    letterscores = {
        'a': 2, 'b': 5, 'c': 3, 'd': 3, 'e': 1, 'f': 5, 'g': 4, 'h': 4, 'i': 2,
        'j': 10, 'k': 6, 'l': 3, 'm': 4, 'n': 2, 'o': 2, 'p': 4, 'q': 'unknown', 'r': 2,
        's': 2, 't': 2, 'u': 4, 'v': 6, 'w': 6, 'x': 9, 'y': 5, 'z': 8
    }

# end class Global

class Wordament:
    # Passed to and set by __init__()
    letters: str

    # Computed from self.letters in __init__()
    # Both are 4x4.
    grid: List[List[str]]
    scores: List[List[int]]

    # Mark what positions have been used. Updated while running
    used: List[List[bool]]

    # A word must match this regex for it ever to be considered.
    # This is (probably) a lot faster than searching the grid.
    wordre: re.Pattern

    def __init__(self, letters):
        self.letters = letters

        self.grid = [[0]*4 for _ in range(4)]
        self.scores = [[0]*4 for _ in range(4)]

        items = set()
        index = 0
        for jj in range(4):
            for ii in range(4):
                # Handle [xy], [xy-], [-xy].
                if letters[index] == '[':
                    endindex = index+1
                    while letters[endindex] != ']':
                        endindex += 1
                    item = letters[index+1:endindex]
                    index = endindex
                    if '-' in item:
                        items.add(item.replace('-', ''))
                        self.grid[ii][jj] = item
                        self.scores[ii][jj] = 12
                    else:
                        items.add(item)
                        self.grid[ii][jj] = item
                        # This score is wrong, but I don't know what it should be.
                        self.scores[ii][jj] = 8
                else:
                    item = letters[index]
                    self.scores[ii][jj] = Global.letterscores[item]
                    items.add(item)
                    self.grid[ii][jj] = item

                index += 1

        self.wordre = re.compile(f'({"|".join(items)})+$')

        # Theory: If all four corners are the same, add 1.
        corner = self.grid[0][0]
        if self.grid[0][3] == corner and self.grid[3][0] == corner and self.grid[3][3] == corner:
            self.scores[0][0] += 1
            self.scores[0][3] += 1
            self.scores[3][0] += 1
            self.scores[3][3] += 1
            logging.info(f'Corner {corner} detected. Using score {self.scores[0][0]}')

        self.used = [[False]*4 for _ in range(4)]
    # end __init__()

    def run(self, word: str) -> int:
        """
        Returns the score of a word or zero if the word isn't in the grid or word isn't valid
        according to the provided letters.
        """
        if not re.match(self.wordre, word):
            return 0

        for jj in range(4):
            for ii in range(4):
                let = self.grid[ii][jj]
                if let[0] == '-':
                    let = let[1:]
                    if not word.endswith(let):
                        continue
                elif let[-1] == '-':
                    let = let[:-1]
                    if not word.startswith(let):
                        continue
                self.used = [[False]*4 for _ in range(4)]
                if word.startswith(let):
                    found, score = self.found_in_grid(word, len(let), (ii,jj))
                    if found:
                        return score + self.scores[ii][jj]
        return 0
    # end run()

    def found_in_grid(self, word: str, wordindex: int, pos: tuple) -> Tuple[bool, int]:
        seq = word[wordindex:]
        #print(f'{seq=} {pos=}\n{self.used}')
        if self.used[pos[0]][pos[1]]:
            return False, 0
        if seq == '':
            return True, 0
        self.used[pos[0]][pos[1]] = True
        #print(f'found_in_grid({seq}, {pos})')
        for npos in neighbors(pos):
            nlet = self.grid[npos[0]][npos[1]]    # neighbor letter
            if nlet[0] == '-':
                nlet = nlet[1:]
                if not word.endswith(nlet):
                    continue
            elif nlet[-1] == '-':
                nlet = nlet[:-1]
                if not word.startswith(nlet):
                    continue
            if seq.startswith(nlet):
                found, score = self.found_in_grid(word, wordindex+len(nlet), npos)
                if found:
                    return True, score + self.scores[npos[0]][npos[1]]
        return False, 0
    # end found_in_grid()

    def print(self):
        """For debugging"""
        print(f'\nLetters: {self.letters}')
        print(f'\nWord Regex: {self.wordre}')
        print('\nGrid')
        print_grid(self.grid)
        print('\nScores')
        print_grid(self.scores)
        print('\nUsed')
        print_grid(self.used)
    # end print()
# end class Wordament


def main(argv):
    parse_arguments(argv[1:])
    setup_logging()

    word2count = read_unigrams(Global.args.unigrams, Global.args.mincount)

    # For now, handle x/y outside the class by running it twice.
    # There's a combinatoric explosion if multiple "/" occur, so
    # only allow one.

    slashindex = Global.args.letters.find('/')

    if slashindex >= 0:
        # Contains /. Check another '/'.
        if Global.args.letters.find('/', slashindex+1) != -1:
            logging.error("Currently, \"/\" can only only appear once")
            sys.exit(1)
        let1 = Global.args.letters[slashindex-1]
        let2 = Global.args.letters[slashindex+1]
        logging.info(f"Detected {let1}/{let2}")
        wordament1 = Wordament(Global.args.letters.replace(f'{let1}/{let2}', let1))
        wordament1.scores[(slashindex-1) % 4][(slashindex-1) // 4] = 20
        wordament2 = Wordament(Global.args.letters.replace(f'{let1}/{let2}', let2))
        wordament2.scores[(slashindex-1) % 4][(slashindex-1) // 4] = 20
        for word, count in word2count.items():
            score = wordament1.run(word)
            if score:
                print(word, word2count[word], score)
            else:
                score = wordament2.run(word)
                if score:
                    print(word, word2count[word], score)
    else:
        # Does not contain x/y
        wordament = Wordament(Global.args.letters)

        for word, count in word2count.items():
            score = wordament.run(word)
            if score:
                print(word, word2count[word], score)
# end main()

def read_unigrams(f, mincount):
    word2count = {}
    for line in f:
        line = line.strip()
        if line == "":
            continue
        count, word = line.split()
        count = int(count)
        if count < mincount:
            continue

        # Skip if three identical letters in a row. This is usually not really a word.
        if re.search(r'([a-z])\1\1', word):
            continue
        word2count[word] = count
    return word2count
# end read_unigrams()


def neighbors(pos: tuple) -> tuple:
    """
    A generator that returns the neighbors of the given tuple.
    """
    for yinc in (-1, 0, 1):
        y = pos[1] + yinc
        for xinc in (-1, 0, 1):
            if xinc == 0 and yinc == 0:
                continue
            x = pos[0] + xinc
            if 0 <= x < 4 and 0 <= y < 4:
                yield (x,y)
# end neighbors


def print_grid(grid, padding=2):
    """
    For debugging.
    """
    width = padding + max([len(str(elem)) for row in grid for elem in row])
    for jj in range(4):
        for ii in range(4):
            print(f'{grid[ii][jj]:<{width}}', end='')
        print()
# end print_grid()


def parse_arguments(strs):
    parser = argparse.ArgumentParser(
        description=f"Description. Version {VERSION}.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='DEBUG',
                        help='Logging level')
    parser.add_argument('-version', '--version', action='version', version=str(VERSION))
    parser.add_argument('letters',
                        help="Letters in wordament")
    parser.add_argument('-unigrams',
                        help="Unigram count file",
                        type=argparse.FileType('r'),
                        default='RC_2017-09.1gram.counts.cumm.filtered')
    parser.add_argument('-mincount',
                        help="Minimum number of times word must appear",
                        type=int,
                        default=1000)
    Global.args = parser.parse_args(strs)
# end parse_arguments()


def setup_logging():
    numeric_level = getattr(logging, Global.args.loglevel, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {Global.args.loglevel}')
    logging.basicConfig(level=numeric_level,
                        format="%(module)s:%(levelname)s:%(asctime)s: %(message)s",
                        datefmt='%Y-%m-%d %H:%M:%S')
# end setup_logging()


if __name__ == "__main__":
    main(sys.argv)


