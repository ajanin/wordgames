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

    for word in Global.args.words:
        word = word.strip()
        if is_candidate(word, Global.args.green, Global.args.yellow, Global.args.gray):
            print(word)
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
