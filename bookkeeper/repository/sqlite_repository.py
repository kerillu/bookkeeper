import sqlite3

from inspect import get_annotations
from bookkeeper.repository.abstract_repository import AbstractRepository, T



class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            col_names = ', '.join(self.fields.keys())
            q = f'CREATE TABLE IF NOT EXISTS {self.table_name} (' \
                f'"pk" INTEGER PRIMARY KEY AUTOINCREMENT, {col_names})'
            cur.execute(q)

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
       #  Получить объект по id 
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
                conditions = ' AND '.join(f"{k} = ?" for k in where.keys())
                values = list(where.values())
                cur.execute(f"SELECT * FROM {self.table_name} WHERE {conditions}", values)
            rows = cur.fetchall()
            objects = []
            for row in rows:
                values = [row[i + 1] for i in range(len(self.fields))]
                obj = self.cls(*values)
                obj.pk = row[0]
                objects.append(obj)
            return objects

    def get_like(self, where: dict[str, any] | None = None) -> list[T]:
        """return list of values that looks like condition in where"""
        if where is None:
            raise ValueError('Where must be not None')
        # function added by power of N_eki 4 ar
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            placeholders = " AND ".join([f"{f} LIKE ?" for f in where.keys()])
            values = list(where.values())
            cur.execute(f"SELECT * FROM {self.table_name} WHERE {placeholders}", values)
            rows = cur.fetchall()
            objects = []
            for row in rows:
                values = [row[i + 1] for i in range(len(self.fields))]
                obj = self.cls(*values)
                obj.pk = row[0]
                objects.append(obj)
            return objects




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
        if self.get(pk) is None:
            raise KeyError('this pk doesnt exist')
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM {self.table_name} WHERE rowid = {pk}")
        con.close()

