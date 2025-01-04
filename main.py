import sys
from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QDialog
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QAction
import sqlite3
from PyQt6.uic import loadUi


db_name = 'coffee.sqlite'
db_name = 'D:/ЯЛ/промыш/db/coffee.sqlite'
role_db = Qt.ItemDataRole.UserRole + 1


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        Dialog.resize(400, 300)


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.initUi()
        self.initDB()
        self.edit_item = None

    def initUi(self):
        self.setWindowTitle('Капучино')
        # Set the table headers
        title_headers = ['ID', 'Название', 'Обжарка', 'Вид', 'Вкус', 'Цена', 'Объем']
        self.tableWidget.setColumnCount(len(title_headers))
        self.tableWidget.setHorizontalHeaderLabels(title_headers)
        for i in range(len(title_headers)):
            self.tableWidget.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tableWidget.setRowCount(0)

        # запрет редактирования таблицы
        self.tableWidget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # выделение только одной строки
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.tableWidget.cellDoubleClicked.connect(self.onCellDoubleClicked)

        appendAction = QAction(QIcon(), 'Добавить', self)
        appendAction.setStatusTip('Добавить запись')
        appendAction.triggered.connect(self.appendRecord)

        menubar = self.menuBar()
        menubar.addAction(appendAction)

    def appendRecord(self):
        dlg = AddEditCoffeeDlg(self, None)
        dlg.exec()

    def modifyRecord(self):
        dlg = AddEditCoffeeDlg(self, self.edit_id)
        dlg.exec()
        self.edit_id = None

    def initDB(self):
        # Подключение к БД
        self.con = sqlite3.connect(db_name)
        # Создание курсора
        cur = self.con.cursor()
        # Выполнение запроса и получение всех результатов
        result = self.con.execute(
            '''SELECT 
            coffee.id, coffee.id, 
            coffee.name, coffee.name, 
            roasting.name, roastingID,
            ground, ground, 
            taste.name, tasteID,
            price, price, 
            volume, volume
            FROM coffee 
            left join roasting on roastingID=roasting.id
            left join taste on tasteID=taste.id
            ''').fetchall()

        self.tableWidget.setRowCount(len(result))
        # Вывод результатов на экран
        ground = ['Молотый', 'В зернах']
        for i, elem in enumerate(result):
            for j in range(0, len(elem), 2):
                new_item = None
                userData = 0
                if j == 3 * 2:
                    new_item = QTableWidgetItem(ground[elem[j]])
                else:
                    new_item = QTableWidgetItem(str(elem[j]))
                # пусть будет для всех элементов, пригодится на будущее
                new_item.setData(role_db, elem[j + 1])
                self.tableWidget.setItem(i, j // 2, new_item)

        self.tableWidget.resizeColumnsToContents()
        self.con.close()

    def onCellDoubleClicked(self, row, column):
        item = self.tableWidget.item(row, 0)
        if item is None:
            return
        self.edit_id = self.tableWidget.item(row, 0).data(role_db)
        self.modifyRecord()


class AddEditCoffeeDlg(QDialog):
    def __init__(self, parent, record_id):
        super().__init__(parent)
        loadUi('addEditCoffeeForm.ui', self)
        if record_id is None:
            self.setWindowTitle('Добавить запись')
            self.button_execute.setText('Добавить')
        else:
            self.setWindowTitle('Изменить запись')
            self.button_execute.setText('Изменить')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
