import datetime
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QMainWindow, QMessageBox
from typing import Any
from bookkeeper.repository.sqlite_repository import SQLiteRepository
from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


class ExpensePresenter:
    """
    Методы:
        update_expense_data - обновить расходы
        show - start point of main window
        handle_expense_add_button_clicked - доавбляет расход при нажатии "Добавить"
    """
    def __init__(self, model: any, view: any, cat_repo, exp_repo):
        self.model = model
        self.view = view
        self.cat_repo = cat_repo
        self.exp_repo = exp_repo
        self.exp_data = None
        self.cat_data = cat_repo.get_all()  # TODO: implement update_cat_data() similar to update_expense_data()
        self.view.on_expense_add_button_clicked(self.handle_expense_add_button_clicked)
#        self.view.on_expense_update_button_clicked(self.handle_expense_update_button_clicked)
        #self.view.on_expense_update_button_clicked(self.handle_expense_update_button_clicked())
        self.view.on_expense_delete_button_clicked(self.handle_expense_delete_button_clicked)
        #self.view.on_category_edit_button_clicked(self.handle_category_edit_button_clicked)
        self.view.on_redactor_add_button_clicked(self.show_redactor_clicked)

        red_w = self.view.get_redactor()
        red_w.on_add_category_clicked(self.add_category_button_clicked)
        red_w.on_delete_category_clicked(self.delete_category_button_clicked)
        #red_w.on_add_budget_clicked(self.add_budget_button_clicked)

    def update_expense_data(self):
        """
        exp_data = [[tup.added_date,
                     tup.amount,
                     tup.category,
                     tup.comment]
                    for tup in self.repos[1].get_all()]
        print(exp_data)
        if not exp_data:
            solo_exp = [[0, 0, '', 'Пока никаких расходов']]
            self.view.set_expense_table(solo_exp)
        else:
            self.view.set_expense_table(exp_data)
        """

        self.exp_data = self.exp_repo.get_all()
        for e in self.exp_data:  #TODO: "TypeError: 'NoneType' object is not iterable" on empty DB
            for c in self.cat_data:
                if c.pk == e.category:
                    e.category = c.name
                    break
        if not self.exp_data:
            solo_exp = [Expense(amount=0,
                                category='',
                                expense_date='',
                                added_date='',
                                comment='Пока никаких расходов',
                                pk=0)]
            self.view.set_expense_table(solo_exp)
        else:
            print(self.exp_data)
            self.view.set_expense_table(self.exp_data)


    def update_category_data(self) -> None:
        self.cat_data = self.cat_repo.get_all()
        cat1 = []
        for c in self.cat_data:
            cat1.append(c.pk)
        cat_set = set(cat1)
        cat2 = list(cat_set)
        print(cat2)
        res2 = []
        for c1 in cat2:
            ada = self.cat_repo.get(c1)
            res2.append(ada)
        print(res2)
        empty = []
        self.view.set_category_dropdown(empty)
        #self.view.set_category_dropdown(res2)


    def show(self):
        self.view.show()
        self.update_expense_data()
        cat_data = self.cat_repo.get_all()
        #cat_data = [[cat.name, cat.parent, cat.pk] for cat in self.repos[0].get_all()]
        #print(cat_data)
        self.view.set_category_dropdown(cat_data)

    def handle_expense_add_button_clicked(self) -> None:
        summ, cat, comment, date = self.view.get_summ_cat_comment_date()
        #cat_pk = self.view.get_cat()
        #comment = self.view.get_comment()
        #summ = self.view.get_summ()
        exp = Expense(amount=float(summ), category=cat, comment=comment, added_date=date)
        self.exp_repo.add(exp)
        self.update_expense_data()


    def handle_expense_delete_button_clicked(self) -> None:
        selected = self.view.get_selected_expenses()
        if selected:
            for e in selected:
                self.exp_repo.delete(e)
            self.update_expense_data()

#        selected = self.view.get_selected_expenses()
#        expense_pk_dict = self.pk_get_all_expense()
#        print(selected)
#        print(expense_pk_dict)
#        if selected:
#            for cat in selected:
#                self.exp_repo.delete(expense_pk_dict[cat])
#        self.update_expense_data()

    """
    def handle_expense_update_button_clicked(self) -> None:
        selected = self.view.get_selected_expenses()
        summ, cat, comment = self.view.get_summ_cat_comment()
        #ad_date = self.view.get_selected_date
        if len(selected) == 1:
            exp = Expense(amount=summ,
                          category=cat,
           #               added_date=ad_date[0],
                          comment=comment,
                          pk=selected)
            self.exp_repo.update(exp)
        else:
            raise AttributeError(f"can not update more than 1 object at one moment ")
        self.update_expense_data()
    """


# TODO: может, добавить кнопку "очистить всё"?

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

#    def handle_category_edit_button_clicked(self):
#        self.view.show_cats_dialog(self.cat_data)

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