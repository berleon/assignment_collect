
from assignment_collect.datastructure import Repository, Student
from subprocess import Popen, PIPE
import subprocess


def test_repostory_clone(tmpdir):
    dir_from = tmpdir.mkdir('from')
    dir_to = tmpdir.mkdir('to')
    assert subprocess.call(['git', 'init'], cwd=str(dir_from)) == 0
    f = dir_from.join('hello.txt')
    f.write("Hello World!")
    assert subprocess.call(['git', 'add', '.'], cwd=str(dir_from)) == 0
    gcommit = ['git', 'commit', '-m', 'Add hello world!']
    assert subprocess.call(gcommit, cwd=str(dir_from)) == 0

    student = Student("Julia", "4534343")
    repo = Repository(str(dir_from), [student])
    repo.clone(str(dir_to))
    assert dir_to.join('hello.txt').check()
    assert dir_to.join('hello.txt').read() == 'Hello World!'


def test_repostory_clone_remote(tmpdir):
    url = "https://github.com/berleon/test.git"
    student = Student("Julia", "4534343")
    repo = Repository(url, [student])
    repo.clone(str(tmpdir))

    assert tmpdir.join('hello.txt').check()
    assert tmpdir.join('hello.txt').read() == 'Hello World!\n'
