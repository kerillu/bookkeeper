from PySide6.QtWidgets import QApplication
from bookkeeper.view.expense_view import MainWindow
from bookkeeper.presenter.expense_presenter import ExpensePresenter
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.repository.sqlite_repository import SQLiteRepository
import sys
import sqlite3

DB_NAME = 'test28.db'

if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = MainWindow()
    model = None

    cat_repo = SQLiteRepository[Category](DB_NAME, Category)
    exp_repo = SQLiteRepository[Expense](DB_NAME, Expense)
    bud_repo = SQLiteRepository[Budget](DB_NAME, Budget)

    def create_bud(bud_repo: SQLiteRepository):

        with sqlite3.connect(DB_NAME) as con:
            cur = con.cursor()
            cur.execute('SELECT * FROM "Budget"')
            p = cur.fetchall()
            #print(p)
            if p == []:
                bud_repo.add(Budget(limit_on=1000))  # spent=0
                bud_repo.add(Budget(limit_on=7000))  # spent=0
                bud_repo.add(Budget(limit_on=30000))  # spent=0
            else:
                None


    create_bud(bud_repo)



    window = ExpensePresenter(model, view, cat_repo, exp_repo, bud_repo)
    window.show()
    app.exec_()