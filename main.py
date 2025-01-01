import sys
from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6.QtCore import QSize, Qt
import sqlite3


db_name = 'coffee.sqlite'
# db_name = 'D:/ЯЛ/промыш/db/coffee.sqlite'


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.initUi()
        self.initDB()

    def initUi(self):
        # Set the table headers
        title_headers = ['ID', 'Название', 'Обжарка', 'Вид', 'Вкус', 'Цена', 'Объем']
        self.tableWidget.setColumnCount(len(title_headers))
        self.tableWidget.setHorizontalHeaderLabels(title_headers)
        for i in range(len(title_headers)):
            self.tableWidget.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tableWidget.setRowCount(0)

    def initDB(self):
        # Подключение к БД
        self.con = sqlite3.connect(db_name)
        # Создание курсора
        cur = self.con.cursor()
        # Выполнение запроса и получение всех результатов
        result = self.con.execute(
            '''SELECT coffee.id, coffee.name, roasting.name, ground, taste.name, price, volume FROM coffee 
            left join roasting on roastingID=roasting.id
            left join taste on tasteID=taste.id
            ''').fetchall()

        self.tableWidget.setRowCount(len(result))
        # Вывод результатов на экран
        ground = ['Молотый', 'В зернах']
        for i, elem in enumerate(result):
            for j in range(len(elem)):
                if j == 3:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(ground[elem[j]]))
                else:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem[j])))

        self.tableWidget.resizeColumnsToContents()
        self.con.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())

