from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QComboBox, QLineEdit, QPushButton, QMainWindow, QMessageBox, QTabWidget
from PySide6 import QtCore, QtWidgets
from bookkeeper.view.categories_view import CategoryDialog
from bookkeeper.view.budge_widget import BudgetWidget
from bookkeeper.repository.abstract_repository import T
from bookkeeper.view.redactor_view import RedactorWindow
from datetime import datetime


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data: list[any], columns: list[str]): #columns: list[str]):
        super(TableModel, self).__init__()
        self._data = data
        self.columns = columns
        #self.header_names = ['Сумма', 'Категория',
        #                    'Дата добавления', 'Дата покупки',
        #                     'Комментарий', 'id']
        #self.header_names = list(data[0].__dataclass_fields__.keys())


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return str(self.columns[section])
            #return super().headerData(section, orientation, role) #str(self.columns[section])


    def data(self, index, role):#index, role):
        if role == QtCore.Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            fields = list(self._data[index.row()].__dataclass_fields__.keys())
            return self._data[index.row()].__getattribute__(fields[index.column()])
            #return self._data[index.row()][index.column()]
        #return None

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0].__dataclass_fields__)#self._data[0])


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.item_model = None

        """связь с окном редактирования"""
        self.redactor_w = RedactorWindow()

        self.setWindowTitle("Программа для ведения бюджета")
        self.setFixedSize(500, 600)

        self.layout = QVBoxLayout()

        """окно для таблицы расходов"""
        self.layout.addWidget(QLabel('Последние расходы'))
        self.expenses_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.expenses_grid)

        """окно для таблицы бюджета"""
        self.layout.addWidget(QLabel('Бюджет'))
        self.budget_grid = QtWidgets.QTableView()
        self.layout.addWidget(self.budget_grid)

        """ээээээ интерфейс, расположение кнопок внизу в сетке 
        (с указанием положения типа ("номер столбца", "номер строки")"""
        self.bottom_controls = QGridLayout()

        """окно для комментария"""
        self.bottom_controls.addWidget(QLabel('Комментарий'), 0, 0)
        self.comment_line_edit = QLineEdit()
        self.bottom_controls.addWidget(self.comment_line_edit, 0, 1)

        """окно для суммы"""
        self.bottom_controls.addWidget(QLabel('Сумма'), 1, 0)
        self.summ_line_edit = QLineEdit()
        summ = self.bottom_controls.addWidget(self.summ_line_edit, 1, 1)  # TODO: добавить валидатор

        """окно для даты"""
        self.bottom_controls.addWidget(QLabel('Дата'), 2, 0)
        self.date_line_edit = QLineEdit()
        summ = self.bottom_controls.addWidget(self.date_line_edit, 2,1)

        """шторка категории"""
        self.bottom_controls.addWidget(QLabel('Категория'), 3, 0)
        self.category_dropdown = QComboBox()
        self.bottom_controls.addWidget(self.category_dropdown, 3, 1)

        """кнопка редактирования"""
        self.edit_button = QPushButton('Редактировать')
        self.bottom_controls.addWidget(self.edit_button, 1, 2)
        self.edit_button.clicked.connect(self.show_cats_dialog)

        """кнопка добавления"""
        self.expense_add_button = QPushButton('Добавить')
        self.bottom_controls.addWidget(self.expense_add_button, 4, 1)

        """кнопка удаления вселенной"""
        self.expense_delete_button = QPushButton('Удалить')
        self.bottom_controls.addWidget(self.expense_delete_button, 2, 2)

#        """кнопка обновления"""
#        self.expense_update_button = QPushButton('Обновить')
#        self.bottom_controls.addWidget(self.expense_update_button, 0, 2)

        # виджет бюджета
#        tab_widget = QTabWidget()
#        budget = BudgetWidget()
#        tab_widget.addTab(budget, "Бюджет")


        # виджет вкладок в качестве центрального виджета главного окна
#        self.setCentralWidget(tab_widget)

        self.bottom_widget = QWidget()
        self.bottom_widget.setLayout(self.bottom_controls)

        self.layout.addWidget(self.bottom_widget)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)

        self.setCentralWidget(self.widget)

    def set_expense_table(self, data):#: list[T]) -> None:
        """таблица расходов"""
        if data:
            self.item_model = TableModel(data, ['Сумма', 'Категория', 'Дата добавления',
                                                'Дата покупки', 'Комментарий', 'id'])
            self.expenses_grid.setModel(self.item_model)
            self.expenses_grid.resizeColumnsToContents()
            grid_width = sum([self.expenses_grid.columnWidth(x) for x in range(0, self.item_model.columnCount(0) + 1)])
            self.setFixedSize(grid_width + 80, 600)


    def set_budget_table(self, data) -> None:
        """making budget table on main window"""
        self.item_model = TableModel(data, ['Бюджет', 'id', 'Потрачено'])
        self.budget_grid.setModel(self.item_model)
        grid_width = sum([self.budget_grid.columnWidth(x) for x in range(0, self.item_model.columnCount(0) + 1)])
        self.setFixedSize(grid_width + 80, 600)

    def set_category_dropdown(self, data):#: list[str]) -> None:
        self.category_dropdown.clear()
        for c in data:
            self.category_dropdown.addItem(c.name, c.pk)
#        self.category_dropdown.clear()
#        self.category_dropdown.addItems([tup[0] for tup in data])


    def on_expense_add_button_clicked(self, slot: any):
        self.expense_add_button.clicked.connect(slot)



#    def on_expense_update_button_clicked(self, slot: any) -> None:
#        """connect to funtion slot after clicking button"""
#        self.expense_update_button.clicked.connect(slot)

    def on_expense_delete_button_clicked(self, slot: any):
        """delete expense when button "удалить" clicked"""
        self.expense_delete_button.clicked.connect(slot)



    def on_redactor_add_button_clicked(self, slot: any) -> None:
        """open new window of redaction"""
        self.edit_button.clicked.connect(slot)

    def get_redactor(self):
        return self.redactor_w

    def _is_valid_summ(self, summ: str) -> bool:
        try:
            float(str(self.summ_line_edit.text()))
            return True
        except ValueError:
            return False


    def get_summ(self) -> float:
        """возвращает сумму"""
        if not self._is_valid_summ(str(self.summ_line_edit.text())):
            message_box = QMessageBox.warning(self,
                                              "Неверный формат количества",
                                              "Количество должно быть в формате числа!")
            return message_box and float(self.summ_line_edit.text())      #summ_float = float(self.summ_line_edit.text())
        else:
            if float(self.summ_line_edit.text()) <= 0:
                message_box = QMessageBox.warning(self,
                                                  "Неверный формат количества",
                                                  "Количество должно быть больше нуля!")
                raise ValueError
            else:
                return float(self.summ_line_edit.text())

    def get_comment(self) -> any:
        """возвращает комментария"""
        return str(self.comment_line_edit.text())

    def get_cat(self) -> any:
        """возвращает категорию"""
        return self.category_dropdown.currentText()

    def get_date(self) -> any:
        """возвращает покупки типа"""
        date_str = str(self.date_line_edit.text())
        if not self._is_valid_date(date_str):
            message_box = QMessageBox.warning(self,
                                              "Неверный формат даты",
                                              "Дата должна быть в формате DD/MM/YYYY!")
            return message_box and datetime.strptime(date_str, '%d/%m/%Y').date()
        else:
            date = datetime.strptime(date_str, '%d/%m/%Y').date()
            return date

    def get_summ_cat_comment_date(self) -> list[any]:
        """возвращает всё сразу"""
        return [self.get_summ(), self.get_cat(), self.get_comment(), self.get_date()]

    def __get_selected_row_indices(self) -> list[int]:
        return list(set([qmi.row() for qmi in self.expenses_grid.selectionModel().selection().indexes()]))

    def get_selected_expenses(self) -> list[int] | None:
        idx = self.__get_selected_row_indices()
        if not idx:
            return None
        return [self.item_model._data[i].pk for i in idx]




    def _is_valid_date(self, date_str: str) -> bool:
        """
        Проверяет, находится ли строка даты в формате "YYYY-MM-DD".
        """
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def show_cats_dialog(self, data):
        if data:
            cat_dlg = CategoryDialog(data)
            cat_dlg.setWindowTitle('Редактирование категорий')
            cat_dlg.setGeometry(300, 100, 600, 300)
            cat_dlg.exec_()