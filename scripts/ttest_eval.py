#!/usr/bin/env python3
import argparse
import re
from collections import OrderedDict, abc
from typing import Any, Dict, Set, Tuple

import numpy as np
import pandas as pd
from irtools.eprint import eprint
from scipy import stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""Run student-t test (scipy.stats.ttest_rel) on paired `trec_eval -q` output, or
        one-way ANOVA test (scipy.stats.f_oneway) if there are more than two groups."""
    )

    parser.add_argument(
        "evals",
        metavar="EVALS",
        nargs="*",
        help="Run `trec_eval -q -m METRIC QREL RUN` to get eval output.",
        type=argparse.FileType("r"),
    )

    parser.add_argument("--precision", type=int, default=4)
    args = parser.parse_args()
    return args


def rbp_parse(line: str) -> Tuple[str, str, np.array]:
    match = re.match(
        r"p= *(\d+\.\d+) *q= *(\w+) *d= *(\w+) *rbp= *(\d+\.\d+) *\+(\d+\.\d+)", line,
    )
    assert match is not None
    rbp_p = match[1]
    qid = match[2]
    depth = match[3]
    rbp_value = float(match[4])
    rbp_res = float(match[5])
    metric = f"rbp_{rbp_p}@{depth}"
    return metric, qid, np.array([rbp_value, rbp_res])


def trec_parse(line: str) -> Tuple[str, str, np.array]:
    splits = line.split()
    metric, qid, value = splits[0], splits[1], np.array([float(splits[2])])
    return metric, qid, value


def format_value(x: np.ndarray, precision: int) -> Any:
    if isinstance(x, float):
        return f"{x:.{precision}f}"
    elif isinstance(x, np.ndarray):
        if x.size == 1:
            return f"{x[0]:.{precision}f}"
        elif x.size == 2:
            return f"{x[0]:.{precision}f} +{x[1]:.{precision}f}"
        else:
            assert False, f"Unsupported format {x}"
    else:
        assert isinstance(x, abc.Sequence)
        return [format_value(cell, precision) for cell in x]


def main() -> None:
    args = parse_args()

    filenames = [x.name for x in args.evals]
    results: Dict[str, Dict[str, Dict[str, np.ndarray]]] = OrderedDict()
    file_metrics: Dict[str, Set[str]] = OrderedDict()
    parse_func = trec_parse
    for eval_ in args.evals:
        for line in eval_:
            if line.startswith("#"):
                continue
            if "rbp=" in line:
                parse_func = rbp_parse

            metric, qid, value = parse_func(line)
            if qid == "all":
                continue
            file_metrics.setdefault(eval_.name, set()).add(metric)
            results.setdefault(metric, OrderedDict())
            results[metric].setdefault(eval_.name, {})
            results[metric][eval_.name][qid] = value

    common_metrics = set.intersection(*list(file_metrics.values()))
    eprint(f"Common metrics: {sorted(common_metrics)}")
    for filename, metrics in file_metrics.items():
        diff = metrics - common_metrics
        if diff:
            eprint(f"{filename}: disregard {sorted(diff)}")

    agg = {}
    data = []
    for metric in sorted(common_metrics):
        file_results = results[metric]
        union = set.union(*[set(x.keys()) for x in file_results.values()])
        inter = set.intersection(*[set(x.keys()) for x in file_results.values()])
        if union != inter:
            eprint(f"{metric} discarded ids: {sorted(union - inter)}")
        for filename in file_results.keys():
            for id_ in union - inter:
                file_results[filename].pop(id_, None)

        qids = sorted(inter)
        agg[metric] = {
            file_: np.mean(list(x.values()), axis=0)
            for file_, x in file_results.items()
        }
        scores = [
            [qid_scores[qid][0] for qid in qids] for qid_scores in file_results.values()
        ]
        if len(args.evals) == 2:
            _, pvalue = stats.ttest_rel(*scores)
        else:
            _, pvalue = stats.f_oneway(*scores)

        str_values = format_value([agg[metric][x] for x in filenames], args.precision)
        data.append((metric, *str_values, format_value(pvalue, args.precision)))

    # Sort by metric names
    data = sorted(data)
    last_column = "p-value" if len(args.evals) == 2 else "p-value(anova)"
    df = pd.DataFrame(
        data,
        columns=["Measure", *[f"Sys{i}" for i in range(len(filenames))], last_column],
    )
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
