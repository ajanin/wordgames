#!/usr/bin/env python3
#
# Enter the guess you've given wordle and wordle's reply, and this program
# will suggest the next guess based on letter counts in the consistent
# remaining words.
#
# Since the current code removes words that aren't consistent before
# computing letter counts, it's "hard mode".

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

    # Load initial words
    words = set()
    for word in Global.args.words:
        word = word.strip()
        words.add(word)

    # Load unigrams
    unigrams = {}
    for line in Global.args.unigrams:
        count, word = line.strip().split()
        unigrams[word] = int(count)

    # Initialize constraints

    # A regular expression that must be exactly 5 letters.
    green = '.....'

    # A set containing the letters that cannot appear.
    gray = set()

    # A list of exactly 5 sets, each containing the letters that cannot
    # be in that location.
    yellow = [set(), set(), set(), set(), set()]

    # A set of containing letters that must appear (that is, letters that
    # were ever yellow or green).
    required_letters = set()

    # These are the letters we've guessed.
    guessed_letters = set()

    # This is used to initialize guess.
    nextguess = 'aeros'

    while True:
        reply = None
        print(f"Enter your guess or wordle's reply to {nextguess}: ", end='')
        guess = input().strip().lower()
        if nextguess != '' and (guess == '' or all((c in 'ybg' for c in guess))):
            print(f"Using {nextguess}")
            reply = guess
            guess = nextguess
        if len(guess) != 5:
            print("The guess must be exactly 5 letters.")
            continue
        guessed_letters.update(guess)
        if reply is None:
            print("Enter Wordle's reply: ", end='')
            reply = input().strip()
        if not re.match(r'[byg]{5}$', reply):
            print("The reply must be exactly 5 letters long consisting of only b, y, or g (for black, yellow, and green).")
            continue

        for ii, r in enumerate(reply):
            c = guess[ii]

            # Wordle will report a letter as gray even if it was previously reported as yellow or
            # green if it's in a different position. So when checking from gray, don't include
            # required letters.

            if r == 'b' and c not in required_letters:
                gray.add(c)
            elif r == 'g':
                if green[ii] != '.' and green[ii] != c:
                    print(f"You are reporting a green {c} at position {ii}, but already reported a green {green[ii]} there.")
                    break
                # TODO: Make sure any yellow are consistent too.
                required_letters.add(c)
                green = green[:ii] + c + green[ii+1:]
            if r == 'y':
                # TODO: Make sure this are consistent.
                required_letters.add(c)
                yellow[ii].add(c)

        logging.info(f"gray {gray}")
        logging.info(f"yellow {yellow}")
        logging.info(f"green {green}")

        # We have new contraints. Remove any word from words that doesn't match the contraints.
        # Keep track of letter counts in the remaining.

        lettercounts = collections.Counter()
        for word in list(words):
            if not is_candidate(word, gray, yellow, green, required_letters):
                words.remove(word)
                lettercounts.update(word)

        # Sort words by unigram counts
        words = sorted(words, key=lambda w: unigrams.get(w, 1), reverse=True)

        if len(words) == 0:
            logging.error("There are no candidates. This shouldn't happen.")
            sys.exit(1)

        if len(words) == 1:
            print(f"Success! {list(words)[0]}")
            sys.exit(0)

        if len(words) < 5:
            print(f"Remaining candidates: {' '.join(words)}")
        else:
            print(f"Remaining candidates: {len(words)}")

        # Remove letters we've guessed already.

        for letter in guessed_letters:
            del lettercounts[letter]

        if len(lettercounts) == 0:
            print("All letters found. Candidates are:")
            print(' ', ' '.join(list(words)))
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


def is_candidate(word, gray, yellow, green, required_letters):
    # Convert gray to a regexp class. If any letter matches, not a candidate.
    if re.search(f"[{''.join(gray)}]", word):
        return False

    # Not a candidate if green doesn't match.
    if not re.match(green, word):
        return False

    # All required letters must be present
    if not required_letters <= set(word):
        return False

    # Not a candidate if any of the yellows are in the wrong place.
    yellowre = ''.join(['.' if not x else f"[^{''.join(x)}]" for x in yellow])
    if yellowre != '.....' and not re.match(yellowre, word):
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
    parser.add_argument('-unigrams',
                        type=argparse.FileType('r'),
                        default='unigram_counts')
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
