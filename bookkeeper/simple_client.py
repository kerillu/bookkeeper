"""
Простой тестовый скрипт для терминала
"""
import os.path
import sqlite3

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.utils import read_tree


db_file = 'test10.db'

cat_repo = SQLiteRepository[Category](db_file, Category)
exp_repo = MemoryRepository[Expense]()


#def create_tab(con):
#    cur = con.cursor()
#    cur.execute('create table if not exists "Category" ('
#                '"id" integer primary key autoincrement, '
#                '"name" text, '
#                '"parent" integer)'
#                )
#    cur.execute('SELECT * FROM "Category"')
#    p = cur.fetchall()
#    print(p)
#   if p == []:
def create_cats(cat_repo: SQLiteRepository):

    cats = '''
        продукты
            мясо
                сырое мясо
                мясные продукты
            сладости
        книги
        одежда
        '''.splitlines()
    with sqlite3.connect(db_file) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM "Category"')
        p = cur.fetchall()
        print(p)
        if p == []:
            Category.create_from_tree(read_tree(cats), cat_repo)
        else: None

create_cats(cat_repo)
#    con.close()

#create_tab(con)

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*cat_repo.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*exp_repo.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = cat_repo.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        exp_repo.add(exp)
        print(exp)


