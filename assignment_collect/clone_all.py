
import argparse
import json
from assignment_collect.datastructure import Repository
import os


def repo_dirname(repo):
    repo_name = repo.url.split(':')[-1]
    prefix = repo_name.split('/')[-2:]
    if prefix[-1].endswith('.git'):
        prefix[-1] = prefix[-1][:-len('.git')]
    lastnames = []
    for student in repo.students:
        lastnames.append(student.name.split(' ')[-1])
    parts = prefix + lastnames
    return "_".join([p.lower() for p in parts])


def clone_all(repositories, to):
    cloned = []
    for repo in repositories:
        repo_name = repo_dirname(repo)
        path = os.path.join(to, repo_name)
        if not os.path.exists(path):
            print("Cloning: {}".format(repo_name))
            cloned.append(repo.clone(path))

    for repo in cloned:
        repo.url = os.path.basename(repo.url)
    return cloned


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=str,
                        help='file with json repository structure')
    parser.add_argument('-t', '--to', type=str,
                        help='clone repositories to this directory')
    parser.add_argument('--list', type=bool, default=False,
                        help='file is a list of repositories')

    args = parser.parse_args()
    with open(args.json) as f:
        if args.list:
            repositories = [Repository(url=url.rstrip('\n'), students=[])
                            for url in f.readlines()]
        else:
            repositories = [Repository(**c) for c in json.load(f)]

    cloned_repos = clone_all(repositories, args.to)
    config = [r.get_config() for r in cloned_repos]
    with open(os.path.join(args.to, 'repos.json'), 'w+') as f:
        json.dump(config, f, ensure_ascii=False)
