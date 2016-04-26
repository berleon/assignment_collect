
import argparse
import json
from assignment_collect.datastructure import Repository
import os


def repo_dirname(repo):
    prefix = repo.url.split('/')[-2:]
    if prefix[-1].endswith('.git'):
        prefix[-1] = prefix[-1][:-len('.git')]
    lastnames = []
    for student in repo.students:
        lastnames.append(student.name.split(' ')[-1])
    parts = prefix + lastnames
    return "_".join([p.lower() for p in parts])


def clone_all(repositories, to):
    return [repo.clone(os.path.join(to, repo_dirname(repo)))
            for repo in repositories]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=str,
                        help='file with json repository structure')
    parser.add_argument('-t,--to', type=str,
                        help='clone repositories to this directory')

    args = parser.parse_args()
    with open(args.json) as f:
        repositories = [Repository(**c) for c in json.load(f)]

    clone_all(repositories, args.to)
