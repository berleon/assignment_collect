from __future__ import print_function

import os
import sys
import subprocess
from assignment_collect.utils import run


def executable_exists(name):
    try:
        devnull = open(os.devnull)
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            return False
    return True


def check_git(directory=None):
    if not executable_exists('git'):
        print("Please install git!", file=sys.stderr)
        sys.exit(1)
    if directory is not None:
        git_root(directory)


def git_remote_v(cwd=None):
    if cwd is None:
        cwd = os.getcwd()
    check_git(cwd)
    stdout, _ = run(['git', 'remote', '-v'], cwd=cwd)
    remote_lines = stdout.decode('utf-8').split('\n')

    remotes = []
    for remote in remote_lines[:-1]:
        remote = remote.replace('\t', ' ')
        name, url, fetch_or_push = remote.split(' ')
        if fetch_or_push == '(push)':
            remotes.append((name, url))

    return remotes


def git_root(directory=None):
    if directory is None:
        current_dir = os.getcwd()
    else:
        current_dir = directory
    while True:
        if os.path.exists(os.path.join(current_dir, '.git')):
            return current_dir
        # step one up
        parent = os.path.dirname(current_dir)
        if parent == current_dir:
            raise Exception("No git repo in {}.".format(directory))
        current_dir = parent


def git_clone(url, dirname):
    check_git()
    run(['git', 'clone', url, dirname])


def git_commit(message, dirname=None):
    if dirname is None:
        dirname = os.getcwd()
    check_git(dirname)
    run(['git', 'commit', '-m', message], cwd=dirname)
