
from subprocess import Popen, PIPE
import os


def run(command, stdin=None, **popen_kwargs):
    p = Popen(command, stdin=PIPE, stdout=PIPE,
              stderr=PIPE, **popen_kwargs)
    if type(stdin) == str:
        stdin = stdin.encode('utf-8')
    stdout, stderr = p.communicate(input=stdin)
    if p.returncode != 0:
        raise Exception(
            "Command failed: {}\nstdout:\n{}\nstderr:\n{}".format(
                ' '.join(command), stdout, stderr))
    return stdout, stderr


def get_subdirs(dirname):
    return [os.path.join(dirname, d) for d in os.listdir(dirname)
            if os.path.isdir(os.path.join(dirname, d))]


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
