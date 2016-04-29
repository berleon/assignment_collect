from subprocess import Popen, PIPE
import json
import os


def run(command):
    p = Popen(command, stdout=PIPE,
              stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        raise ValueError(
            "Command failed: {}\nstdout:\n{}\nstderr:\n{}".format(
                ' '.join(command), stdout, stderr))


class Datastructure:
    def get_config(self):
        raise NotImplemented()

    def to_json(self):
        return json.dumps(self.get_config())

    @classmethod
    def from_json(cls, json_str):
        config = json.loads(json_str)
        return cls(**config)

    def __eq__(self, other):
        return self.get_config() == other.get_config()


class Student(Datastructure):
    def __init__(self, name, matnr, email='', zedat_name=''):
        self.name = name
        self.email = email
        self.matnr = matnr
        self.zedat_name = zedat_name

    @property
    def firstname(self):
        return " ".join(self.name.split(" ")[:-1])

    @property
    def lastname(self):
        return self.name.split(" ")[-1]

    def get_config(self):
        return {
            'name': self.name,
            'matnr': self.matnr,
            'email': self.email,
            'zedat_name': self.zedat_name
        }


class Repository(Datastructure):
    def __init__(self, url, students):
        self.url = url
        self.students = self._maybe_get_students_from_config(students)

    def name(self):
        return os.path.basename(self.url)

    @staticmethod
    def _maybe_get_students_from_config(students):
        students_return = []
        for student in students:
            if type(student) == dict:
                students_return.append(Student(**student))
            elif type(student) == Student:
                students_return.append(student)
            else:
                raise ValueError("Wrong type for student: {}, {}".format(
                    type(student), student))
        return students_return

    def clone(self, dirname):
        run(['git', 'clone', self.url, dirname])
        return Repository(dirname, self.students)

    def get_config(self):
        return {
            'url': self.url,
            'students': [s.get_config() for s in self.students]
        }
