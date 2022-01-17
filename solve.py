#!/usr/bin/env python3
#

import argparse
import collections
import logging
import re
import sys

VERSION = 0.1


class Global:
    """Stores globals. There should be no instances of Global."""

    # Command line arguments
    args = None

# end class Global


def main(argv):
    parse_arguments(argv[1:])
    setup_logging()

    lettercounts = collections.Counter()
    candidates = set()
    words = set()

    for word in Global.args.words:
        word = word.strip()
        words.add(word)
        if is_candidate(word, Global.args.green, Global.args.yellow, Global.args.gray):
            lettercounts.update(word)
            candidates.add(word)

    if len(candidates) == 1:
        print(f"Success: {list(candidates)[0]}")
        sys.exit(0)

    if len(candidates) == 0:
        logging.error("No candidates found. This shouldn't happen!")
        sys.exit(1)

    logging.info(f"Number of candidates: {len(candidates)}")

    # Remove any we have info about.
    for letter in (set(Global.args.green) |
                   Global.args.gray |
                   set(''.join(Global.args.yellow)) - set('.')):
        del lettercounts[letter]

    if len(lettercounts) == 0:
        print("All letters found. Candidates are:")
        print(' ', ' '.join(list(candidates)))
        sys.exit(0)

    # String of the letters we don't have info about, sorted by
    # how frequent they are in the candidates.

    letters = ''.join([x[0] for x in lettercounts.most_common()])

    logging.info(f"Informative letters: {letters}")

    # Find a word that has any many letters we don't have info
    # about as possible, prefering letters that are common in
    # the candidates.

    nextguess = None

    # If we can find a word where we don't have info on any of
    # its letters, use it. If there are many such words, start
    # with ones that have more common letters.
    
    if len(letters) >= 5:
        for n in range(5, len(letters)):
            word, count = find_word_with_letters(words, letters[0:n])
            if count == 5:
                nextguess = word
                break

    if nextguess is None:
        word, count = find_word_with_letters(words, letters)
        nextguess = word

    logging.info(f"Informative letters in {nextguess}: {count}")
    print(f"Next guess: {nextguess}")
# end main()


def is_candidate(word, green, yellow, gray):
    """
    Arguments:

    word - Input string
    green - Regular expression that must be five characters. E.g. g...n
    yellow - A list of give entries. Each entry is a character set that
             must match. E.g. ['rn', '.', '.', 'g', '.'] means r and n
             appear, but cannot be in the initial position, and g appears
             but cannot be in the 4th position.
    gray - A set containing letters that cannot appear. E.g. {'x', 'f', 'a'}
           means x, f, and a cannot appear anywhere.
    """

    # Regular expression matching anything in gray. That is, if gray
    # contains "abc", then match the regexp [abc].

    grayre = f"[{''.join(gray)}]"

    # The set of all letters that occur anywhere in yellow.  All these
    # letters must appear in the word somewhere.  For example, if
    # -yellow . . ae . ab was passed, yellowset will contain
    # {'a', 'b', 'e'}

    yellowset = {c for c in ''.join(yellow) if c != '.'}

    # This regular expression fails to matches if yellows appear in
    # the wrong place. For example, if -yellow . . ae . ab was passed,
    # yellowre will be '..[^ae].[^ab]'.

    yellowre = ''.join([x if x == '.' else f'[^{x}]' for x in yellow])

    # Not a candidate if any gray matches.
    if re.search(grayre, word):
        # print("gray failed")
        return False

    # Not a candidate if any green doesn't match.
    if not re.match(Global.args.green, word):
        # print("green failed")
        return False

    # Not a candidate if yellowset isn't a subset of the letters in word.
    if not yellowset <= set(word):
        # print(f"yellowset failed '{yellowset}'")
        return False

    # Not a candidate if yellows are in the wrong place.
    if yellowre != '.....' and not re.match(yellowre, word):
        # print("yellowre failed")
        return False

    return True
# end is_candidate()


def find_word_with_letters(words, letters):
    bestword = None
    bestcount = -1
    for word in words:
        count = len(set(word) & set(letters))
        if count > bestcount:
            bestcount = count
            bestword = word

    return bestword, bestcount
# end find_word_with_letters()


def parse_arguments(strs):
    parser = argparse.ArgumentParser(
        description=f"Description. Version {VERSION}.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='DEBUG',
                        help='Logging level')
    parser.add_argument('-version', '--version', action='version', version=str(VERSION))
    parser.add_argument('-words',
                        type=argparse.FileType('r'),
                        default='words')
    parser.add_argument('-yellow',
                        nargs=5,
                        required=True)
    parser.add_argument('-green',
                        required=True)
    parser.add_argument('-gray',
                        type=set,
                        required=True)
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
