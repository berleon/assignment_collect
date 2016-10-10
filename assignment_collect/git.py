import os
from assignment_collect.utils import run


def git_remote_v(cwd=None):
    stdout, _ = run(['git', 'remote', '-v'], cwd=cwd)
    remote_lines = stdout.decode('utf-8').split('\n')

    remotes = []
    for remote in remote_lines[:-1]:
        remote = remote.replace('\t', ' ')
        name, url, fetch_or_push = remote.split(' ')
        if fetch_or_push == '(push)':
            remotes.append((name, url))

    return remotes


def git_root():
    current_dir = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current_dir, '.git')):
            return current_dir

        # step one up
        current_dir = os.path.dirname(current_dir)


def git_clone(url, dirname):
    run(['git', 'clone', url, dirname])


def git_commit(message, dirname=None):
    run(['git', 'commit', '-m', message], cwd=dirname)
