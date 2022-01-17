#!/usr/bin/env python3
#

import argparse
import logging
import random
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

    words = read_words(Global.args.wordfile)
    word = random.sample(words, 1)[0]
    word = 'panic'

    print(f'"{word}"')

    for guessi in range(10):
        sys.stdout.write(f"Guess {guessi+1}: ")
        guess = input()
        if guess == word:
            print("Correct!")
            break
        for ii in range(len(guess)):
            if guess[ii] == word[ii]:
                sys.stdout.write(f"\033[92m{guess[ii]}\033[0m ")
            elif guess[ii] in word:
                sys.stdout.write(f"\033[33m{guess[ii]}\033[0m ")
            else:
                sys.stdout.write(f"{guess[ii]} ")
        print()
# end main()


def read_words(f):
    words = set()
    for line in f:
        line = line.strip()
        words.add(line)
    return words
# end read_words()


def parse_arguments(strs):
    parser = argparse.ArgumentParser(
        description=f"Description. Version {VERSION}.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        help='Logging level')
    parser.add_argument('-version', '--version', action='version', version=str(VERSION))
    parser.add_argument('-wordfile', help='Word file', type=argparse.FileType('r'), default='words')
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
