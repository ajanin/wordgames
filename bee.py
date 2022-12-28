#!/usr/bin/env python3
#

import argparse
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

    word2count = read_unigrams(Global.args.unigrams, Global.args.letters, 0)

    # Show pangrams from most common to least
    print("Pangrams:")
    letterset = set(Global.args.letters)
    for word, count in sorted(word2count.items(), key=lambda item: item[1], reverse=True):
        if set(word) == letterset:
            del word2count[word]
            print(word, count)

    # Show everything else from longest word to shortest.
    print("\nAll:")
    for word, count in sorted(word2count.items(), key=lambda item: len(item[0]), reverse=True):
        if count > Global.args.mincount:
            print(word, count)
# end main()


def read_unigrams(f, letters, mincount):
    word2count = {}
    wordre = re.compile(f'[{letters}]*{letters[0]}[{letters}]*$')
    for line in f:
        line = line.strip()
        if line == "":
            continue
        count, word = line.split()
        count = int(count)
        if count < mincount:
            continue
        if not re.match(wordre, word):
            continue

        # Skip if three identical letters in a row.
        if re.search(r'([a-z])\1\1', word):
            continue
        word2count[word] = count
    return word2count
# end read_unigrams()


def parse_arguments(strs):
    parser = argparse.ArgumentParser(
        description=f"Description. Version {VERSION}.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-loglevel',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default='WARNING',
                        help='Logging level')
    parser.add_argument('-version', '--version', action='version', version=str(VERSION))
    parser.add_argument('letters',
                        help="Letters in bee")
    parser.add_argument('-unigrams',
                        help="Unigram count file",
                        type=argparse.FileType('r'),
                        default='RC_2017-09.1gram.counts.cumm.filtered')
#                        default='RC_2017-09.1gram.counts.cumm.sorted')
    parser.add_argument('-mincount',
                        help="Minimum number of times word must appear",
                        type=int,
                        default=200)
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
