
import argparse
import json
from assignment_collect.datastructure import Repository
import os
import csv
import re
import traceback

_find_ex_regex = re.compile('ex(\d+):(\d+(\.\d)?)', re.MULTILINE)


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
                ex, points_for_ex, _ = match
                points_for_ex = float(points_for_ex)
                ex = int(ex) - 1
                assert ex < len(points)
                assert ex >= 0
                assert points_for_ex < max_points[ex]
                assert points_for_ex >= 0
                assert ex not in ex_found, "Multiple ex{}".format(ex+1)
                points[ex] = points_for_ex
                ex_found.add(ex)

        grades_fname = os.path.join(repo.url, 'grades.txt')

        grade_line = "{}:\t{}\tsum({})\n".format(
            notebook_name, ", ".join(map(str, points)), sum(points))

        if os.path.exists(grades_fname):
            with open(grades_fname, 'r') as f:
                grade_enteries = list(f.readlines())
            for i, line in enumerate(grade_enteries):
                if line.startswith(notebook_name):
                    grade_enteries[i] = grade_line
        else:
            grade_enteries = []

        if grade_line not in grade_enteries:
            grade_enteries.append(grade_line)

        with open(grades_fname, 'w+') as f:
            f.write("".join(grade_enteries))

    except:
        print("Exception in: {}".format(repo.name()))
        traceback.print_exc()

    return [[s.zedat_name, s.zedat_name, s.lastname,
             s.firstname, sum(points)] for s in repo.students]


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
