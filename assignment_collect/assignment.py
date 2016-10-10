
from __future__ import print_function

import sys
import os
import json
import shutil
import csv

import click
from assignment_collect.datastructure import Repository, RepositoryCollection, Student
from assignment_collect.utils import run, get_subdirs, mkdir_p
from assignment_collect.git import git_root, git_remote_v, git_clone


def repo_json_fname():
    return Repository.magic_file(git_root())


def get_repo():
    if not os.path.exists(repo_json_fname()):
        print("This repository has not been initialized!", file=sys.stderr)
        print("Please run `assignmnt init` first!", file=sys.stderr)
        sys.exit(1)
    with open(repo_json_fname()) as f:
        return Repository(**json.load(f))


def save_repo(repo):
    with open(repo_json_fname(), 'w') as f:
        json.dump(repo.get_config(), f)
    run(["git", "add", repo_json_fname()], cwd=git_root())
    basename = os.path.basename(repo_json_fname())
    print("Please commit the {} file.".format(basename))


@click.group()
def main():
    pass


class StudentOption(click.Option):
    def __init__(self, param_decls=None, max_students=1,
                 init_repo=True,
                 **attrs):
        super(StudentOption, self).__init__(param_decls, **attrs)
        self.max_students = max_students
        self.init_repo = init_repo

    def prompt_for_value(self, ctx):
        """This is an alternative flow that can be activated in the full
        value processing if a value does not exist.  It will prompt the
        user until a valid value exists and then returns the processed
        value as result.
        """
        # Calculate the default before prompting anything to be stable.
        # If this is a prompt for a flag we need to handle this
        # differently.
        def prompt(prompt_str, type=str):
            return click.prompt(prompt_str, value_proc=type)

        def parse_matrnr(x):
            try:
                return int(x)
            except ValueError:
                print("Got invalid Matrikelnumber: {}".format(x), file=sys.stderr)
                print("Aborted!", file=sys.stderr)
                sys.exit(1)
        students = []

        if self.init_repo and os.path.exists(repo_json_fname()):
            print("This repository allready has been initialized!", file=sys.stderr)
            print("You can add more students with `assignmnt add_student`!", file=sys.stderr)
            print("Or you can delete the `.repo.json` file.", file=sys.stderr)
            sys.exit(1)
        if not self.init_repo:
            repo = get_repo()
            if len(repo.students) == self.max_students:
                print("Cannot add more students. Maximal {} students are allowed "
                      "to work at one assignment.".format(self.max_students), file=sys.stderr)
                print("Abort!", file=sys.stderr)

        for i in range(self.max_students):
            first_name = prompt("Enter Student First Name")
            last_name = prompt("Enter Student Last Name")
            matrnr = prompt("Enter Matrikelnumber for {} {}".format(first_name, last_name),
                            type=parse_matrnr)
            students.append(Student(first_name, last_name, matrnr))
            last_iteration = i + 1 == self.max_students
            if (not last_iteration and
                    not click.confirm("Do you want to enter another student?", True)):
                break
            if last_iteration:
                print("Reached maximum limit of students.")

        return students


@main.command()
@click.option('--student', prompt=True, init_repo=False, max_students=1, cls=StudentOption)
def add_student(student):
    with open(repo_json_fname()) as f:
        repo = Repository(**json.load(f))
    repo.students.append(repo)
    save_repo(repo)


@main.command()
@click.option('--student', prompt=True, max_students=2, cls=StudentOption)
def init(student):
    for s in student:
        print(s)

    remotes = git_remote_v()

    if len(remotes) == 1:
        print("Found only one remote: {} at {}".format(*remotes[0]), file=sys.stderr)
        print("You should have two remotes. One remote to pull the assignments from.\n"
              "And one remote where you push our solved assignments.", file=sys.stderr)
        print("Make sure you add your remote and then rerun this program.", file=sys.stderr)
        print("Abort!", file=sys.stderr)
        sys.exit(1)

    remotes_prompt = ["[{}] {} {}".format(i, name,  url)
                      for i, (name, url) in enumerate(remotes)]
    remotes_prompt.append(
        "Select your remote repository. The instructure will use this repository"
        " to collect your assignments. [0-{}]".format(len(remotes) - 1))

    while True:
        try:
            remote_idx = click.prompt("\n".join(remotes_prompt), value_proc=int)
            break
        except ValueError:
            print("Please enter a number from 0-{}".format(len(remotes) - 1))

    _, url = remotes[remote_idx]
    repo = Repository(url, student, git_root())
    save_repo(repo)
    print("Initialized repository!")


@main.command()
@click.argument("number", type=int)
def check(number):
    def _check(bool_expr, error, ok=None):
        if bool_expr:
            if ok is not None:
                print(ok)
        else:
            print(error, file=sys.stderr)
            print("Not valid! Abort!", file=sys.stderr)
            sys.exit(1)

    repo = get_repo()
    fname = repo.get_assignment_filename(number)
    _check(os.path.exists(fname),
           "Assignment file does not exists: {}".format(fname),
           "Assignment does exists: {}".format(fname))

    _check(os.path.isfile(fname),
           "Assignment is not a file: {}".format(fname))
    # maybe check modification time: os.path.getmtime(fname)
    print("Seems to be fine! Your solutions must be in this notebook.")


@main.command("clone_all")
@click.option("-o", "--output", help='clone repositories to this directory',
              type=click.Path(file_okay=False, resolve_path=True))
@click.argument("repolist", type=click.Path(dir_okay=False, exists=True, resolve_path=True))
def clone_all(output, repolist):
    """
    Clones all repositories in file REPOLIST and performs a sanity check.
    """
    def repo_dirname(url):
        repo_name = url.split(':')[-1]
        parts = repo_name.split('/')[-2:]
        if parts[-1].endswith('.git'):
            parts[-1] = parts[-1][:-len('.git')]
        return "_".join([p.lower() for p in parts])

    with open(repolist) as f:
        urls = [url.rstrip('\n') for url in f.readlines()]

    mkdir_p(output)

    subdirs = get_subdirs(output)
    allready_cloned = {}
    for subdir in subdirs:
        for _, url in git_remote_v(subdir):
            allready_cloned[url] = subdir

    no_longer_in_list = set(allready_cloned.keys()) - set(urls)
    if len(no_longer_in_list) > 0:
        print("Following urls were allready cloned but are now"
              " no longer present in the given list.")
        for url in no_longer_in_list:
            print("    {}".format(url))
        if click.confirm("Do you wish to remove them?"):
            for url in no_longer_in_list:
                if os.path.exists(allready_cloned[url]):
                    shutil.rmtree(allready_cloned[url])

    urls_to_clone = set(urls) - set(allready_cloned.keys())

    repo_dirs = list(set(allready_cloned.values()))
    for url in urls_to_clone:
        path = os.path.join(output, repo_dirname(url))
        print("Cloning {} to {}".format(url, path))
        git_clone(url, path)
        repo_dirs.append(path)

    for repo_dir in repo_dirs:
        repo = Repository.from_dir(repo_dir)
        repo.sanity_check()

    repo_colllection = RepositoryCollection('.', output)
    repo_colllection.save(output)


@main.command("complete_student_data")
@click.option('-c', '--csv', type=click.Path(dir_okay=False), help="CSV export from the KVV.")
@click.argument("repos_dir", type=click.Path(file_okay=False, exists=True, resolve_path=True),
                required=False)
def complete_student_data(csv, repos_dir=None):
    """
    Completes the students data with a csv export of the students data from the KVV.
    REPOS_DIR can be set to the directory where the cloned repositories are located.
    Default is the current working directory.

    The column order of the csv export must be:

        lastname, firstname, matnr, email, zedat_name
    """
    if repos_dir is None:
        repos_dir = os.getcwd()
    repo_collection = RepositoryCollection.from_dir(repos_dir)
    students_list = repo_collection.get_complete_students(csv)
    for repo in repo_collection.repos():
        repo.complete_students(students_list)
        repo.save()


def _parse_max_points(points):
    return list(map(int, points.split(',')))


@main.command("collect_points")
@click.option("--points", type=_parse_max_points,
              prompt=True,
              help="Number of points per exercise. Seperated by comma e.g. `1,4,5`")
@click.argument("number", type=str)
def collect_points(number, points):
    try:
        repo_collection = RepositoryCollection.from_dir(os.getcwd())
    except FileNotFoundError:
        print("`assignmnt collect_points` must be run in the directory, where "
              "the cloned repositories are located. ", file=sys.stderr)
        sys.exit(1)
    with open('grades_{:02d}.csv'.format(number), 'w+') as f:
        writer = csv.writer(f)
        writer.writerow(("Student ID", "Student Name",
                         "Assignment [{}]".format(sum(points))))
        for repo in repo_collection.repos():
            rows = repo.collect_points(number, points)
            for row in rows:
                writer.writerow(row)
