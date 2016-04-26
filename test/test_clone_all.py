
from assignment_collect.clone_all import clone_all
from assignment_collect.datastructure import Repository, Student


def test_clone_all(tmpdir):
    students0 = [
            Student("Madhuri Madelief", matnr="1043"),
            Student("Sanjana Julia", matnr="0939")
        ]
    students1 = [
            Student("Treasure Presley", matnr="6041")
        ]
    repositories = [
        Repository("https://github.com/berleon/test.git", students=students0),
        Repository("https://github.com/berleon/test.git", students=students1),
    ]
    repositories_cloned = clone_all(repositories, str(tmpdir))
    assert repositories_cloned[0].url.endswith("berleon_test_madelief_julia")
    assert repositories_cloned[1].url.endswith("berleon_test_presley")

    assert repositories_cloned[0].students == students0
    assert repositories_cloned[1].students == students1

    for repo in repositories_cloned:
        assert repo.url.startswith(str(tmpdir))
