#! /usr/bin/env python3
"""
 strip output of IPython Notebooks
 add this as `.git/hooks/pre-commit`
 to run every time you commit a notebook

strip outputs from an IPython Notebook Opens a notebook, strips its output, and
writes the outputless version to the original file.  Useful mainly as a git
filter or pre-commit hook for users who don't want to track output in VCS.
This does mostly the same thing as the `Clear All Output` command in the
notebook UI.
LICENSE: Public Domain
Adapted from: https://gist.github.com/minrk/6176788
"""

import subprocess
from subprocess import PIPE, Popen
import io
import argparse
import os

try:
    # Jupyter >= 4
    from nbformat import read, write, NO_CONVERT
except ImportError:
    # IPython 3
    try:
        from IPython.nbformat import read, write, NO_CONVERT
    except ImportError:
        # IPython < 3
        from IPython.nbformat import current

        def read(f, as_version):
            return current.read(f, 'json')

        def write(nb, f):
            return current.write(nb, f, 'json')


def get_rev():
    command = "git rev-parse --verify HEAD".split(" ")
    if subprocess.call(command, stdin=PIPE, stdout=PIPE, stderr=PIPE) == 0:
        return 'HEAD'
    else:
        return '4b825dc642cb6eb9a060e54bf8d69288fbee4904'


def get_notebooks(against):
    command = "git diff-index -z --cached {} --name-only".format(against)
    p = Popen(command.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    assert p.returncode == 0, \
        "Command failed: {}\nstdout:\n{}\nstderr:\n{}"\
            .format(command, output, err)
    files = [binary_fname.decode('utf8')
             for binary_fname in output.split(b'\x00')]
    return set([f for f in files if f.endswith(".ipynb")])


def run_as_git_hook():
    against = get_rev()
    for notebook_fname in get_notebooks(against):
        print("Stripping output from: {}".format(notebook_fname))
        strip_output(notebook_fname)

    command = "git diff-index --check --cached {} --".format(against)
    subprocess.call(command.split(" "))


def _cells(nb):
    """Yield all cells in an nbformat-insensitive manner"""
    if nb.nbformat < 4:
        for ws in nb.worksheets:
            for cell in ws.cells:
                yield cell
    else:
        for cell in nb.cells:
            yield cell


def strip_output(filename):
    """strip the outputs from a notebook"""

    with io.open(filename, 'r', encoding='utf8') as f:
        nb = read(f, as_version=NO_CONVERT)

    nb.metadata.pop('signature', None)
    for cell in _cells(nb):
        if 'outputs' in cell:
            cell['outputs'] = []
        if 'prompt_number' in cell:
            cell['prompt_number'] = None
    with io.open(filename, 'w', encoding='utf8') as f:
        write(nb, f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Strips the output from a notebook')
    parser.add_argument('file', type=str, default='', nargs='?',
                        help='remove the output from this notebook')
    args = parser.parse_args()
    if args.file == '':
        run_as_git_hook()

    else:
        fname = args.file
        if not os.path.exists(fname):
            print("File {} does not exists.".format(fname))
        strip_output(fname)
