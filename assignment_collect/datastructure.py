import subprocess
from subprocess import Popen, PIPE
import json

class Student():
    def __init__(self, name, matnr):
        self.name = name
        self.matnr = matnr


class Repository():
    def __init__(self, url, students):
        self.url = url
        self.students = students

    def clone(self, dirname):
        command = ['git', 'clone', self.url, dirname]
        p = Popen(command, stdout=PIPE,
                  stderr=PIPE)
        stdout, stderr = p.communicate()
        assert p.returncode == 0, \
            "Command failed: {}\nstdout:\n{}\nstderr:\n{}"\
                .format(' '.join(command), stdout, stderr)

    def get_config(self):
        return {
            'url': self.url,
            'students': self.students
        }


def repositories_to_json(repositories):
    config = [repo.get_config() for repo in repositories]
    return json.dumps(config)
