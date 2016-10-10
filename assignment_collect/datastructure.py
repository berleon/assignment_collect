import json
import os
import re
import csv
import traceback
from assignment_collect.utils import run, get_subdirs
from assignment_collect.git import git_root


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
    def __init__(self, firstname, lastname, matnr, email='', zedat_name=''):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.matnr = matnr
        self.zedat_name = zedat_name

    @property
    def name(self):
        return self.firstname + " " + self.lastname

    def get_config(self):
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'matnr': self.matnr,
            'email': self.email,
            'zedat_name': self.zedat_name
        }

    def __str__(self):
        ss = "Name: {}, Matr: {}".format(self.name, self.matnr)
        if self.email:
            ss += ", Email: " + self.email
        if self.zedat_name:
            ss += ", Zedat Name: " + self.zedat_name
        return ss


class Repository(Datastructure):
    def __init__(self, url, students, repo_root):
        self.url = url
        self.students = self._maybe_get_students_from_config(students)
        self.repo_root = repo_root

    def name(self):
        return os.path.basename(self.repo_root)

    MAGIC_FILE = '.assignment_repo.json'

    @staticmethod
    def magic_file(dirname=None):
        if dirname is None:
            dirname = git_root()
        return os.path.join(dirname, Repository.MAGIC_FILE)

    @staticmethod
    def from_dir(dirname):
        if not os.path.exists(Repository.magic_file(dirname)):
            raise Exception("No repository found at {}. Missing file {}."
                            .format(dirname, Repository.MAGIC_FILE))
        with open(Repository.magic_file(dirname)) as f:
            config = json.load(f)
            config['repo_root'] = dirname
            return Repository(**config)

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
        return Repository(self.url, self.students, dirname)

    def get_config(self):
        return {
            'url': self.url,
            'students': [s.get_config() for s in self.students],
            'repo_root': self.repo_root
        }

    def save(self, output_dir=None):
        if output_dir is None:
            output_dir = self.repo_root
        fname = self.magic_file(output_dir)
        with open(fname, 'w') as f:
            json.dump(self.get_config(), f)

    def root(self):
        return self.repo_root

    def get_assignment_filename(self, number):
        return os.path.join(self.root(), "assignments/assignment_{:02d}.ipynb".format(number))

    def sanity_check(self, max_students=2):
        if len(self.students) == 0:
            print("No students are set in repo: {}".format(self.url))
        if len(self.students) > max_students:
            print("Too many students are set in repo: {}".format(self.url))

    def complete_students(self, students):
        updated_students = []
        for student in self.students:
            if student.matnr in students:
                updated_students.append(students[student.matnr])
            else:
                print("Did not find data for student {}!".format(student))
                updated_students.append(student)
        self.students = updated_students

    _find_ex_regex = re.compile('ex(\d+):(\d+(\.\d)?)', re.MULTILINE)

    def collect_points(self, assignment_number, max_points):
        notebook_fname = self.get_assignment_filename(assignment_number)

        points = max_points.copy()
        ex_found = set()

        try:
            if not os.path.exists(notebook_fname):
                print("File does not exists: {}. Giving zero points.".format(notebook_fname))
                points = [0 for _ in points]
            else:
                with open(notebook_fname, 'r') as f:
                    notebook = f.read()
                    match_found = False
                    for match in self._find_ex_regex.findall(notebook):
                        match_found = True
                        ex, points_for_ex, _ = match
                        points_for_ex = float(points_for_ex)
                        ex = int(ex) - 1
                        assert ex < len(points)
                        assert ex >= 0
                        assert points_for_ex < max_points[ex]
                        assert points_for_ex >= 0
                        assert ex not in ex_found, "Multiple ex{}".format(ex+1)
                        points[ex] = points_for_ex
                        ex_found.add(ex)
                    if not match_found:
                        print(notebook_fname)
                        assert 'ex:top' in notebook

            grades_fname = os.path.join(self.root(), 'grades.txt')

            grade_line = "#{}:\t{}\tsum({})\n".format(
                assignment_number, ", ".join(map(str, points)), sum(points))

            if os.path.exists(grades_fname):
                with open(grades_fname, 'r') as f:
                    grade_enteries = list(f.readlines())
                for i, line in enumerate(grade_enteries):
                    if line.startswith("#{}".format(assignment_number)):
                        grade_enteries[i] = grade_line
            else:
                grade_enteries = []

            if grade_line not in grade_enteries:
                grade_enteries.append(grade_line)

            with open(grades_fname, 'w+') as f:
                f.write("".join(grade_enteries))

        except:
            print("Exception in: {}".format(self.name()))
            traceback.print_exc()

        return [[s.zedat_name,
                 "{} {}".format(s.lastname, s.firstname),
                 sum(points)] for s in self.students]


class RepositoryCollection(Datastructure):
    def __init__(self, repos_dir, path, students_csv=None):
        self.repos_dir = repos_dir
        self.path = path
        self.students_csv = students_csv

    MAGIC_NAME = '.assignment_repo_collection.json'

    @staticmethod
    def magic_file(dirname):
        return os.path.join(dirname, Repository.MAGIC_FILE)

    @staticmethod
    def from_dir(dirname):
        fname = RepositoryCollection.magic_file(dirname)
        with open(fname) as f:
            config = json.load(f)
            config['path'] = dirname
            return RepositoryCollection(**config)

    def save(self, output_dir):
        fname = self.magic_file(output_dir)
        with open(fname, 'w') as f:
            json.dump(self.get_config(), f)

    def repos(self):
        for subdir in get_subdirs(self.path):
            try:
                yield Repository.from_dir(subdir)
            except Exception:
                continue

    def get_complete_students(self, students_csv=None):
        if students_csv is None and self.students_csv is None:
            raise Exception("No students_csv file given.")

        if students_csv is None:
            students_csv = self.students_csv

        students = {}
        with open(students_csv, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                lastname, firstname, matnr, email, zedat_name = row
                matnr = int(matnr)
                students[matnr] = Student(firstname, lastname, matnr, email, zedat_name)
        return students

    def get_config(self):
        return {
            'students_csv': self.students_csv,
            'repos_dir': self.repos_dir,
        }
