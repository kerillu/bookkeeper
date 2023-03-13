import datetime
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QMainWindow, QMessageBox
from typing import Any
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category
from bookkeeper.models.budget import Budget
from bookkeeper.view.expense_view import MainWindow

BUDGET_LIST = {"День": 1, "Неделя": 2, "Месяц": 3}
class ExpensePresenter:
    """
    Методы:
        update_expense_data - обновить расходы
        show - start point of main window
        handle_expense_add_button_clicked - доавбляет расход при нажатии "Добавить"
    """
    def __init__(self, model: any, view: any, cat_repo, exp_repo, bud_repo):
        self.model = model
        self.view = view
        self.cat_repo = cat_repo
        self.exp_repo = exp_repo
        self.bud_repo = bud_repo
        self.bud_data = None
        self.exp_data = None
        self.cat_data = cat_repo.get_all()
        self.view.on_expense_add_button_clicked(self.handle_expense_add_button_clicked)
        self.view.on_expense_delete_button_clicked(self.handle_expense_delete_button_clicked)
        self.view.on_redactor_add_button_clicked(self.show_redactor_clicked)

        red_w = self.view.get_redactor()
        red_w.on_add_category_clicked(self.add_category_button_clicked)
        red_w.on_delete_category_clicked(self.delete_category_button_clicked)
        red_w.on_add_budget_clicked(self.add_budget_button_clicked)

    def update_expense_data(self):

        self.exp_data = self.exp_repo.get_all()
        for e in self.exp_data:  #TODO: "TypeError: 'NoneType' object is not iterable" on empty DB
            for c in self.cat_data:
                if c.pk == e.category:
                    e.category = c.name
                    break
        if not self.exp_data:
            solo_exp = [Expense(amount='',
                                category='',
                                expense_date='',
                                added_date='',
                                comment='Пока никаких расходов',
                                pk='')]
            self.view.set_expense_table(solo_exp)
        else:
            print(self.exp_data)
            self.view.set_expense_table(self.exp_data)


    def update_category_data(self) -> None:
        cat_data = self.cat_repo.get_all()
        self.view.set_category_dropdown(cat_data)

    def update_budget_data(self) -> None:
        """updates budget"""
        bud_data = [[bud.limit_on] for bud in self.bud_repo.get_all()]
        today = f"{datetime.datetime.utcnow():%d-%m-%Y %H:%M}"
        week_day = datetime.datetime.utcnow().weekday() + 1


        week_dates = [f"{datetime.datetime.utcnow()-datetime.timedelta(i):%d-%m-%Y %H:%M}"
                      for i in range(week_day)]
        week_data: list[any] = []
        for date in week_dates:
            week_data = week_data+self.bud_repo.get_like({"added_date": f"{date[:10]}%"})
        print(week_data)
        today_data = [float(day.amount)
                      for day in self.bud_repo.get_like({"added_date": f"{today[:10]}%"})]
        week_data = [float(day.amount) for day in week_data]
        month_data = [float(m.amount)
                      for m in self.bud_repo.get_like({"added_date": f"%{today[2:10]}%"})]
        print(bud_data)
        data =[
            Budget(pk=1,   limit_on=bud_data[0][0], added_date=sum(today_data)), #spent=''),
            Budget(pk=2,   limit_on=bud_data[1][0], added_date=sum(week_data)),#spent=''),
            Budget(pk=3,   limit_on=bud_data[2][0], added_date=sum(month_data)) #spent='')
        ]
        self.view.set_budget_table(data)

    def show(self):
        self.view.show()
        self.update_expense_data()
        self.update_budget_data()
        cat_data = self.cat_repo.get_all()
        #cat_data = [[cat.name, cat.parent, cat.pk] for cat in self.repos[0].get_all()]
        #print(cat_data)
        self.view.set_category_dropdown(cat_data)

    def handle_expense_add_button_clicked(self) -> None:
        summ, cat, comment, date = self.view.get_summ_cat_comment_date()
        exp = Expense(amount=float(summ), category=cat, comment=comment, added_date=date)
        self.exp_repo.add(exp)
        self.update_expense_data()


    def handle_expense_delete_button_clicked(self) -> None:
        selected = self.view.get_selected_expenses()
        if selected:
            for e in selected:
                self.exp_repo.delete(e)
            self.update_expense_data()


    def pk_get_all_expense(self) -> dict[str, int]:
        """returning pk of chosen expenses"""
        result = {f"{c.added_date} "
                  f"{c.amount} "
                  f"{c.category} "
                  f"{c.comment}": c.pk for c in self.exp_repo.get_all()}
        return result


    def show_redactor_clicked(self, checked: Any) -> None:
        """show redactor window"""
        red_w = self.view.get_redactor()
        if red_w.isVisible():
            red_w.hide()
        else:
            red_w.show()



    def add_category_button_clicked(self) -> None:
        """add new caregory in category"""
        redactor_view = self.view.get_redactor()
        new_cat = Category(redactor_view.get_add_category())
        self.cat_repo.add(new_cat)
        self.update_category_data()

    def delete_category_button_clicked(self) -> None:
        """deleting category in category"""
        redactor_view = self.view.get_redactor()
        cat_list = {cat.name: cat.pk for cat in self.cat_repo.get_all()}
        cat_delete = redactor_view.get_delete_category()
        self.cat_repo.delete(cat_list[cat_delete])
        self.update_category_data()

    def add_budget_button_clicked(self) -> None:
        """ adding new limit in budget"""
        redactor_view = self.view.get_redactor()
        new_bud = redactor_view.get_selected_bud()
        bud_amount = redactor_view.get_add_budget()
        bud = Budget(limit_on=bud_amount, pk=BUDGET_LIST[new_bud]) #spent=0
        self.bud_repo.update(bud)
        self.update_budget_data()