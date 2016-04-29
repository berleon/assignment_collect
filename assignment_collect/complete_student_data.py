
import argparse
import json
from assignment_collect.datastructure import Repository, Student
import os
import csv


def complete_student_data(csv_fname, repositories):
    students = {}
    with open(csv_fname, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            firstname, lastname, matnr, email, zedat_name = row
            name = " ".join([firstname, lastname])
            students[matnr] = Student(name, matnr, email, zedat_name)

    updated_repos = []
    for repo in repositories:
        updated_students = []
        for student in repo.students:
            if student.matnr in students:
                updated_students.append(students[student.matnr])
            else:
                updated_students.append(student)
        updated_repos.append(Repository(repo.url, updated_students))
    return updated_repos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv", type=str,
                        help='path to students csv file')
    parser.add_argument('--json', type=str, default='repos.json',
                        help='path to a json file with the repo structure')
    parser.add_argument('--to', type=str,
                        help='where to write complete json file')
    args = parser.parse_args()
    assert os.path.exists(args.json)
    assert os.path.exists(args.csv)
    with open(args.json) as f:
        config = json.load(f)
        repositories = [Repository(**c) for c in config]
    updated_repos = complete_student_data(args.csv, repositories)
    config = [r.get_config() for r in updated_repos]
    with open(os.path.join(args.to), 'w+') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
