#!/usr/bin/env python3
import argparse
import sys
import os

from irtools.cleanit import cleanit


def parse_arguments():
    def int_comma(line):
        parsed = [int(x) - 1 for x in str(line).split(',')]
        if any(x < 0 for x in parsed):
            raise argparse.ArgumentTypeError("fields are numbered from 1")
        return parsed

    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-d', '--delimiter', default='\t', help='default to \\t')
    parser.add_argument(
        '-j',
        '--threads',
        type=int,
        default=os.cpu_count() // 2,
        help='number of threads, default to half of cpu count')
    parser.add_argument(
        '-f',
        '--field',
        type=int_comma,
        help='one-based field index to process, e.g. 1,2,3.')
    parser.add_argument(
        '--no-lower',
        action='store_true',
        help='not convert to lower case if specified')
    parser.add_argument(
        '--keep-nonalnum',
        action='store_true',
        help=('override the default behavior of '
              'keeping only English alphabet and numbers'))

    return parser.parse_args()


def main():
    args = parse_arguments()
    lines = cleanit(sys.stdin, args.threads, args.delimiter, args.field,
                    not args.no_lower, not args.keep_nonalnum, '\n')
    sys.stdout.writelines(lines)


if __name__ == '__main__':
    main()
