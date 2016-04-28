
import argparse
import json
from assignment_collect.datastructure import Repository, run
import os
import csv
import re
import traceback

_find_ex_regex = re.compile('ex(\d+):(\d+)', re.MULTILINE)


def collect_points_from_repo(repo, notebook_name, max_points):
    notebook_fname = os.path.join(repo.url, 'assignments',
                                  notebook_name + '.ipynb')

    if not os.path.exists(notebook_fname):
        print("File does not exists: {}".format(notebook_fname))
        return []

    points = max_points.copy()
    ex_found = set()

    try:
        with open(notebook_fname, 'r') as f:
            nb = f.read()
            for match in _find_ex_regex.findall(nb):
                ex, points_for_ex = [int(m) for m in match]
                ex -= 1
                assert ex < len(points)
                assert ex >= 0
                assert points_for_ex < max_points[ex]
                assert points_for_ex >= 0
                assert ex not in ex_found, "Multiple ex{}".format(ex+1)
                points[ex] = points_for_ex
                ex_found.add(ex)
    except:
        print("Exception in: {}".format(repo.name()))
        traceback.print_exc()

    return [[s.name, s.matnr, sum(points)] for s in repo.students]


def collect_points(repos, notebook, max_points):
    with open(notebook + '_grades.csv', 'w+') as f:
        writer = csv.writer(f)
        for repo in repos:
            rows = collect_points_from_repo(repo, notebook, max_points)
            for row in rows:
                writer.writerow(row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("assignment", type=str,
                        help='name of the assignment to collect')
    parser.add_argument('--json', type=str, default='repos.json',
                        help='path to a json file with the repo structure')
    parser.add_argument('--points', type=str, default='10',
                        help='number of points per exercise')
    args = parser.parse_args()
    points = [int(p) for p in args.points.split(',')]
    assert os.path.exists(args.json)
    with open(args.json) as f:
        config = json.load(f)
        repositories = [Repository(**c) for c in config]
    collect_points(repositories, args.assignment, points)
