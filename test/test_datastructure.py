
from assignment_collect.datastructure import Repository, Student


def test_repository_json():
    url = "https://github.com/berleon/test.git"
    student = Student("Julia", "Jpj", "4534343")
    repo = Repository(url, [student], "/tmp/repo")
    json_repo = Repository.from_json(repo.to_json())
    assert repo == json_repo
