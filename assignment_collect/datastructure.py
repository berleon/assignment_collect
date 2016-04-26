from subprocess import Popen, PIPE
import json


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
    def __init__(self, name, matnr):
        self.name = name
        self.matnr = matnr

    def get_config(self):
        return {
            'name': self.name,
            'matnr': self.matnr
        }


class Repository(Datastructure):
    def __init__(self, url, students):
        self.url = url
        self.students = self._maybe_get_students_from_config(students)

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
        command = ['git', 'clone', self.url, dirname]
        p = Popen(command, stdout=PIPE,
                  stderr=PIPE)
        stdout, stderr = p.communicate()
        assert p.returncode == 0, \
            "Command failed: {}\nstdout:\n{}\nstderr:\n{}"\
                .format(' '.join(command), stdout, stderr)

        return Repository(dirname, self.students)

    def get_config(self):
        return {
            'url': self.url,
            'students': [s.get_config() for s in self.students]
        }
