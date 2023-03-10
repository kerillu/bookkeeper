import sqlite3

from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T

def mtob(cls: any, fields: dict[any, any], values: str) -> any:
    res = object.__new__(cls)
    if values is None:
        return None
    for attr, val in zip(fields.keys(), values):
        setattr(res, attr, val)
    setattr(res, 'pk', values[-1])
    return res


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            p = ' '.join([f"{field} TEXT," for field in self.fields])
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS "
                f"{self.table_name} ({p} "
                f"pk INTEGER PRIMARY KEY)"
                )
        con.close()


    def add(self, obj: T) -> int:
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"SELECT 1 FROM {self.table_name} WHERE pk=?", (obj.pk,))
            if cur.fetchone():
                raise sqlite3.IntegrityError("Duplicate primary key")
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f"INSERT INTO  {self.table_name} ({names}) VALUES ({p})", values)
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk


    def get(self, pk: int) -> T | None:
        """ Получить объект по id """
        with sqlite3.connect(self.db_file) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            q = f'SELECT * FROM {self.table_name} WHERE pk = {pk}'
            row = cur.execute(q).fetchone()
        con.close()

        if row is None:
            return None

        values = {k: row[k] for k in row.keys()}
        return self.cls(**values)


    def get_all(self, where: dict[str, any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            if where is None:
                cur.execute(f"SELECT * FROM {self.table_name}")
            else:
                conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
                values = list(where.values())
                cur.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}", values)
            rows = cur.fetchall()
            res = [mtob(self.cls, self.fields, row) for row in rows]
        con.close()
        return res


    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """
#        if obj.pk ==0 :
#            raise ValueError('attempt to update object with unknown primary key')
        with sqlite3.connect(self.db_file) as con:
            names = ', '.join(f"{f} = ?" for f in self.fields)
            values = [getattr(obj, x) for x in self.fields]
            values.append(obj.pk)
            cur = con.cursor()
            cur.execute(f'UPDATE {self.table_name} SET {names} WHERE pk = ?', values)
            if cur.rowcount == 0:
                raise KeyError(f"No {self.cls.__name__} with pk = {obj.pk} found")
        con.close()


    def delete(self, pk: int) -> None:
        """ Удалить запись """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f' DELETE FROM {self.table_name} WHERE pk = ?', (pk,))
            if cur.rowcount == 0:
                raise KeyError(f"No {self.cls.__name__} with pk = {pk} found")
        con.close()

