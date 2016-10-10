
from __future__ import print_function
import os

import pytest
from assignment_collect.utils import run, get_subdirs
from assignment_collect.datastructure import Repository, RepositoryCollection
from assignment_collect.git import git_remote_v, git_commit
from assignment_collect.assignment import clone_all, complete_student_data


@pytest.fixture
def outdir():
    from py.path import local
    path = local("test").join("out")
    if not path.ensure(dir=True):
        path.mkdir()
    return path


@pytest.fixture
def remote_url():
    return 'git@github.com:test/test.git'


@pytest.fixture
def git_repo(tmpdir, remote_url):
    run(['git', 'init', str(tmpdir)])
    run(['git', 'remote', 'add', 'origin',
         remote_url], cwd=str(tmpdir))
    return tmpdir


def test_get_remotes(git_repo, remote_url):
    remotes = git_remote_v(cwd=str(git_repo))
    assert len(remotes) == 1
    assert remotes[0] == ('origin', remote_url)
    upstream_url = 'git@github.com:upstream/upstream.git'

    run(['git', 'remote', 'add', 'upstream', upstream_url], cwd=str(git_repo))
    remotes = git_remote_v(cwd=str(git_repo))
    assert len(remotes) == 2
    assert remotes[0] == ('origin', remote_url)
    assert remotes[1] == ('upstream', upstream_url)


def test_assignment_init_fails_with_one_remote(git_repo):
    os.chdir(str(git_repo))
    stdin = "Max\n"
    stdin += "\n"
    stdin += "4565254\n"
    stdin += "n\n"   # only one student
    stdin += "0\n"   # remote index
    print(stdin)
    with pytest.raises(Exception):
        run(['assignment', 'init'], stdin)


def init_assignment(repo, matrnr="456524"):
    os.chdir(str(repo))
    upstream_url = 'git@github.com:upstream/upstream.git'
    run(['git', 'remote', 'add', 'upstream', upstream_url])
    stdin = "Max\n"
    stdin += "Nix\n"
    stdin += "{}\n".format(matrnr)
    stdin += "n\n"   # only one student
    stdin += "1\n"   # remote index
    run(['assignment', 'init'], stdin)


def test_assignment_init(git_repo):
    init_assignment(str(git_repo))
    assert os.path.exists(Repository.magic_file(str(git_repo)))


def test_assignment_clone_all(tmpdir):
    first = tmpdir.mkdir('first')
    git_repo(first, str(first))
    init_assignment(str(first))
    git_commit("init commit", str(first))
    assert first.exists()

    second = tmpdir.mkdir('second')
    git_repo(second, str(second))
    init_assignment(str(second))
    git_commit("init commit", str(second))
    assert second.exists()
    print(str(first))
    print(str(second))
    repolist = tmpdir.join('repolist.txt')
    with repolist.open('w') as f:
        f.writelines(map(lambda x: str(x) + '\n', [first, second]))
    print(str(tmpdir.join('cloned_repos')), str(repolist))
    try:
        clone_all(['--output', str(tmpdir.join('cloned_repos')), str(repolist)],
                  prog_name="clone_all")
    except SystemExit:
        pass

    for subdir in get_subdirs(str(tmpdir.join('cloned_repos'))):
        assert os.path.exists(Repository.magic_file(subdir))

    assert os.path.exists(
        RepositoryCollection.magic_file(str(tmpdir.join('cloned_repos'))))


def test_assignment_complete_student_data(tmpdir):
    first = tmpdir.mkdir('first')
    git_repo(first, str(first))
    init_assignment(str(first), matrnr=4145235)
    git_commit("init commit", str(first))

    repolist = tmpdir.join('repolist.txt')
    with repolist.open('w') as f:
        f.writelines(map(lambda x: str(x) + '\n', [first]))

    repos_dir = str(tmpdir.join('cloned_repos'))
    try:
        clone_all(['--output', repos_dir, str(repolist)],
                  prog_name="clone_all")
    except SystemExit:
        pass

    students_csv = str(tmpdir.join("students.csv"))
    with open(students_csv, 'w') as f:
        print('"Schulz","Michael","4145235","no@example.com","no"', file=f)
        print('"Ritz","Franz","4455098","franz@example.com","franz"', file=f)

    try:
        complete_student_data(
            ['--csv', students_csv, repos_dir],
            prog_name="complete_student_data"
        )

    except SystemExit:
        pass

    repo_collection = RepositoryCollection.from_dir(repos_dir)
    repos = list(repo_collection.repos())
    assert len(repos) == 1
    assert len(repos[0].students) == 1
    student = repos[0].students[0]
    assert student.firstname == 'Michael'
    assert student.lastname == 'Schulz'
    assert student.matnr == 4145235
