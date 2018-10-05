#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
from operator import itemgetter


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)


def parse_file_weight(s):
    if ':' in s:
        f, w = s.split(':')
    else:
        f = s
        w = 1
    return (f, float(w))


def float_comma_list(s):
    return [float(w) for w in s.split(',')]


def parse_args():
    parser = argparse.ArgumentParser(
        description='Filter spams from run files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument

    parser.add_argument(
        'run',
        type=Path,
        nargs='+',
        metavar='RUN',
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--weight',
        '-w',
        type=float_comma_list,
        metavar='WEIGHT',
    )

    group.add_argument('--sweep', '-s', action='store_true')

    args = parser.parse_args()
    if args.weight is not None and len(args.weight) != len(args.run):
        parser.error('Please specify the same number of weights as runs')

    return args


def fuse(run_weight_list, output_fd):
    qno_scores = {}
    for (run, weight) in run_weight_list:
        for line in run.read_text().splitlines():
            qno, _, docno, _, score, _ = line.split()
            qno_scores.setdefault(qno, {}).setdefault(docno, 0)
            qno_scores[qno][docno] += weight * float(score)

    qno_scores = sorted(
        [(qno, sorted(doc_scores.items(), key=itemgetter(1)))
         for qno, doc_scores in qno_scores.items()],
        key=lambda qs: float(qs[0]))

    current_rank = {}
    lines = []
    for qno, rank_list in qno_scores:
        for docno, score in rank_list:
            current_rank.setdefault(qno, 1)
            lines.append('{qno} Q0 {docno} {rank} {score:.5f} linear\n'.format(
                qno=qno, docno=docno, rank=current_rank[qno], score=score))
            current_rank[qno] += 1

    output_fd.writelines(lines)


def sum_to_number(candidates, n, target):
    if n == 1:
        return [[target]] if target in candidates else []

    ans = []
    for current in candidates:
        sub_ans = sum_to_number(candidates, n - 1, target - current)
        ans.extend([[current] + a for a in sub_ans])
    return ans


def main():
    args = parse_args()

    if args.sweep:
        for wts in sum_to_number(range(0, 11), len(args.run), 10):
            wts = [float(w) / 10.0 for w in wts]
            output = '_'.join(str(w) for w in wts) + '.run'
            with open(output, 'w') as f:
                fuse(zip(args.run, wts), f)
            eprint(output)
    else:
        fuse(zip(args.run, args.weight), sys.stdout)


if __name__ == '__main__':
    main()