import pytest
import sqlite3
from bookkeeper.repository.sqlite_repository import SQLiteRepository
#from bookkeeper.models.category import Category
from dataclasses import dataclass




@pytest.fixture
def test_class():
    @dataclass
    class Test:
        name: str = 'abs'
        pk: int = 0
        parent = str()

    return Test

@pytest.fixture
def repo(tmp_path, test_class):
    db_file = tmp_path / 'test0.db'
    r = SQLiteRepository(str(db_file), test_class)
    yield r

def test_crud(repo, test_class):
    obj = test_class('Яблоко')
    pk = repo.add(obj)
    assert obj.pk == pk

    assert repo.get(pk) == obj

    obj2 = test_class('Банан', pk)
    repo.update(obj2)
    assert repo.get(pk) == obj2

    repo.delete(pk)
    assert repo.get(pk) is None

def test_add_gens_pk(repo, test_class):
    obj = test_class('Keril')
    pk = repo.add(obj)
    assert obj.pk == pk
    assert pk > 0

def test_dubadd_of_pk_raises_error(repo, test_class):
    obj = test_class('Velik')
    pk = repo.add(obj)
    obj2 = test_class('Skate', pk)
    with pytest.raises(sqlite3.IntegrityError):
        repo.add(obj2)

def test_get_returns_none_missingpk(repo, test_class):
    assert repo.get(123) is None

def test_delete_falls_missingpk(repo, test_class):
    with pytest.raises(Exception):
        repo.delete(123)

def test_get_all_return_all(repo, test_class):
    obj1 = test_class('velik')
    obj2 = test_class('skate')
    repo.add(obj1)
    repo.add(obj2)
    objs = repo.get_all()
    assert obj1 in objs
    assert obj2 in objs

def test_get_all_filter(repo, test_class):
    obj1 = test_class('velik', 1)
    obj2 = test_class('skate', 2)
    obj3 = test_class('velik', 3)
    repo.add(obj1)
    repo.add(obj2)
    repo.add(obj3)
    objs = repo.get_all(where={'name': 'velik'})
    assert obj1 in objs
    assert obj2 not in objs
    assert obj3 in objs


def test_cannot_update_without_pk(repo, test_class):
    obj = test_class('Велосипед')
    with pytest.raises(KeyError):
        repo.update(obj)