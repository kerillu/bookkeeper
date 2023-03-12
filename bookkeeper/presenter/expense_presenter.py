import datetime
from typing import Any

from bookkeeper.models.expense import Expense
from bookkeeper.models.category import Category


class ExpensePresenter:
    """
    Методы:
        update_expense_data - обновить расходы
        show - start point of main window
        handle_expense_add_button_clicked - доавбляет расход при нажатии "Добавить"
    """
    def __init__(self, model, view, repo: list[any]):
        self.model = model
        self.view = view
        self.repos = repo
#        self.exp_repo = exp_repo
#        self.exp_data = None
#        self.cat_data = cat_repo.get_all()  # TODO: implement update_cat_data() similar to update_expense_data()
        self.view.on_expense_add_button_clicked(self.handle_expense_add_button_clicked)
        #self.view.on_expense_update_button_clicked(self.handle_expense_update_button_clicked())
        self.view.on_expense_delete_button_clicked(self.handle_expense_delete_button_clicked)
        #self.view.on_category_edit_button_clicked(self.handle_category_edit_button_clicked)
        self.view.on_redactor_add_button_clicked(self.show_redactor_clicked)

        red_w = self.view.get_redactor()
        red_w.on_add_category_clicked(self.add_category_button_clicked)
        red_w.on_delete_category_clicked(self.delete_category_button_clicked)
        #red_w.on_add_budget_clicked(self.add_budget_button_clicked)

    def update_expense_data(self):

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
        self.view.set_expense_table(self.exp_data)
        """

    def update_category_data(self) -> None:
        """update categories menu"""
        cat_data = [[cat.name, cat.parent, cat.pk] for cat in self.repos[0].get_all()]
        # return cat_data
        self.view.set_category_dropdown(cat_data)

    def show(self):
        self.view.show()
        self.update_expense_data()
        cat_data = [[cat.name, cat.parent, cat.pk] for cat in self.repos[0].get_all()]
        print(cat_data)
        self.view.set_category_dropdown(cat_data)

    def handle_expense_add_button_clicked(self) -> None:
        summ, cat, comment = self.view.get_summ_cat_comment()
        #cat_pk = self.view.get_cat()
        #comment = self.view.get_comment()
        #summ = self.view.get_summ()
        exp = Expense(amount=float(summ), category=cat, comment=comment)
        #exp = Expense(int(summ), cat_pk, str(comment))
        self.repos[1].add(exp)
        self.update_expense_data()


    def handle_expense_delete_button_clicked(self) -> None:
        selected = self.view.get_selected_expenses()
        expense_pk_dict = self.pk_get_all_expense()
        if selected:
            for cat in selected:
                self.repos[1].delete(expense_pk_dict[cat])
        self.update_expense_data()
        #selected = self.view.get_selected_expenses()
        #print(selected)
        #for exp in selected:
            #expense_pk_dict = self.pk_get_all_expense()
            #keys = list(expense_pk_dict.keys())
            #print(keys)
            #for i in keys:
                #print(i)
                #self.repos[1].delete(expense_pk_dict[i])
        #self.update_expense_data()
        """
        if selected:
            for e in selected:
                self.exp_repo.delete(e)
            self.update_expense_data()
        """

    def pk_get_all_expense(self) -> dict[str, int]:
        """returning pk of chosen expenses"""
        result = {f"{c.added_date} "
                  f"{c.amount} "
                  f"{c.category} "
                  f"{c.comment}": c.pk for c in self.repos[1].get_all()}
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
        self.repos[0].add(new_cat)
        self.update_category_data()

    def delete_category_button_clicked(self) -> None:
        """deleting category in category"""
        redactor_view = self.view.get_redactor()
        cat_list = {cat.name: cat.pk for cat in self.repos[0].get_all()}
        cat_delete = redactor_view.get_delete_category()
        self.repos[0].delete(cat_list[cat_delete])
        self.update_category_data()