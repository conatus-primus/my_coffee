import sys
from PyQt6 import uic  # Импортируем uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QDialog, QMessageBox
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon, QAction, QIntValidator
import sqlite3
from PyQt6.uic import loadUi


db_name = 'coffee.sqlite'
db_name = 'D:/YL/my_coffee/coffee.sqlite'
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
        # Подключение к БД
        self.con = sqlite3.connect(db_name)
        # закачка таблицы
        self.updateTableFromDB(None)

    def initUi(self):
        self.setWindowTitle('Капучино')

        # разбираемся с таблицей
        title_headers = ['ID', 'Название', 'Обжарка', 'Помол', 'Вкус', 'Цена', 'Объем']
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

        # разбираемся с меню
        appendAction = QAction(QIcon(), 'Добавить', self)
        appendAction.setStatusTip('Добавить запись')
        appendAction.triggered.connect(self.appendRecord)

        menubar = self.menuBar()
        menubar.addAction(appendAction)

    def appendRecord(self):
        dlg = AddEditCoffeeDlg(self, None)
        dlg.exec()

    def modifyRecord(self, record_id_edit):
        dlg = AddEditCoffeeDlg(self, record_id_edit)
        dlg.exec()

    def updateTableFromDB(self, record_id_focus):
        # Выполнение запроса и получение всех результатов
        result = self.con.execute('''
            SELECT 
            coffee.id, coffee.id, 
            coffee.name, coffee.name, 
            roasting.name, roastingID,
            ground.name, groundID, 
            taste.name, tasteID,
            price, price, 
            volume, volume
            FROM coffee 
            left join roasting on roastingID=roasting.id
            left join taste on tasteID=taste.id
            left join ground on groundID=ground.id
            ''').fetchall()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(len(result))
        # Вывод результатов на экран
        for i, elem in enumerate(result):
            for j in range(0, len(elem), 2):
                new_item = None
                new_item = QTableWidgetItem(str(elem[j]))
                # пусть будет для всех элементов, может пригодится на будущее
                new_item.setData(role_db, elem[j + 1])
                self.tableWidget.setItem(i, j // 2, new_item)
                if j == 0 and record_id_focus is not None and record_id_focus == elem[j]:
                    self.tableWidget.setCurrentItem(new_item)

        self.tableWidget.resizeColumnsToContents()
        if self.tableWidget.currentItem() is None:
            self.tableWidget.setCurrentItem(self.tableWidget.item(len(result) - 1, 0))

    def onCellDoubleClicked(self, row, column):
        item = self.tableWidget.item(row, 0)
        if item is None:
            return
        self.modifyRecord(self.tableWidget.item(row, 0).data(role_db))

    def closeEvent(self, event):
        if event:
            self.con.close()
            event.accept()
        else:
            self.close()

class AddEditCoffeeDlg(QDialog):
    def __init__(self, parent, record_id):
        super().__init__(parent)
        self.record_id = record_id
        loadUi('addEditCoffeeForm.ui', self)

        # ограничим ввод числами
        val_price = QIntValidator(self)
        val_price.setRange(0, 99999)
        self.line_price.setValidator(val_price)

        # ограничим ввод числами
        val_volume = QIntValidator(self)
        val_volume.setRange(0, 100 * 1000)
        self.line_volume.setValidator(val_volume)

        # корректируем в зависимости от функциональности
        if record_id is None:
            self.edit = False
            self.setWindowTitle('Добавить запись')
            self.button_execute.setText('Добавить')
            self.label.hide()
            self.line_id.hide()
        else:
            self.edit = True
            self.setWindowTitle('Изменить запись')
            self.button_execute.setText('Изменить')
            self.label.show()
            self.line_id.show()
        self.button_execute.clicked.connect(self.doAction)

        # заполняем все контролы запросом из бд
        self.readDB(record_id)

    def doAction(self):
        try:
            # проверить заполнение всех полей
            if self.line_name is None or self.line_name.text().strip() == '':
                raise ValueError('Не задано наименование!')
            if self.combo_roasting.currentIndex() == -1:
                raise ValueError('Выберите обжарку!')
            if self.combo_ground.currentIndex() == -1:
                raise ValueError('Выберите тип помола!')
            if self.combo_taste.currentIndex() == -1:
                raise ValueError('Выберите вкус!')
            if self.line_price is None or self.line_price.text().strip() == '' or \
                    int(self.line_price.text().strip()) == 0:
                raise ValueError('Не задана цена!')
            if self.line_volume is None or self.line_volume.text().strip() == '' or \
                    int(self.line_volume.text().strip()) == 0:
                raise ValueError('Не задан объем!')

            # все прошло удачно сохранимся
            self.saveToDB()
            # обновим основную таблицу
            # прямо скажем не очень красиво но ладно, пусть так
            self.parent().updateTableFromDB(self.record_id)
            # закначиваем с этим окном
            self.close()

        except ValueError as e:
            x = str(e)
            msg = QMessageBox(self)
            msg.setWindowTitle("Ввод данных")
            msg.setText(str(e))
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.exec()

    # заполняем все контролы запросом из бд
    def readDB(self, record_id):
        edit_record = None
        if record_id is not None:
            record = self.parent().con.execute(
                '''SELECT 
                name,                             
                roastingID,             
                groundID,               
                tasteID,                
                price,      
                volume          
                FROM coffee 
                where id=? 
                ''', (record_id,)).fetchall()

            # если что-то пошло не так то сделаем добавление
            if len(record) == 0:
                self.readDB(self, None)
                return
            else:
                edit_record = record[0]

        # заполняем список обжарки, помола, вкуса
        controlList = \
            [(self.combo_roasting, 'roasting', 1), (self.combo_ground, 'ground', 2), (self.combo_taste, 'taste', 3)]

        for value in controlList:
            # Выполнение запроса и получение всех результатов
            result = self.parent().con.execute(f'SELECT id, name from {value[1]} order by name').fetchall()

            # неопределенные значения
            unknownList = dict()
            # счетчик - не используем enumarate так как пропускаем
            i = 0
            for elem in result:
                # сохраним неизвестные значения
                if elem[0] == 0:
                    unknownList[value[0]] = elem
                    continue
                value[0].addItem(elem[1])
                value[0].setItemData(i, elem[0], role_db)
                if edit_record is not None and elem[0] == edit_record[value[2]]:
                    value[0].setCurrentIndex(i)
                i += 1

            # ставим фокус на неизвестное если не было ничего выбрано
            if value[0] in unknownList:
                unknown = unknownList[value[0]]
                value[0].addItem(unknown[1])
                value[0].setItemData(i, unknown[0], role_db)
                if record_id is None:
                    value[0].setCurrentIndex(i)

        # заполняем остальные поля
        if record_id is not None:
            self.line_id.setText(str(record_id))
            self.line_price.setText(str(edit_record[4]))
            self.line_volume.setText(str(edit_record[5]))
            self.line_name.setText(str(edit_record[0]))

    # сохраним в бд то что наредактировали
    def saveToDB(self):
        # здесь уже гарантированно хорошие данные ничего не проверяем
        # имя
        name = self.line_name.text().strip()
        # обжарка точно задана !
        roastingID = self.combo_roasting.itemData(self.combo_roasting.currentIndex(), role_db)
        # вид
        groundID = self.combo_ground.itemData(self.combo_ground.currentIndex(), role_db)
        # вкус
        tasteID = self.combo_taste.itemData(self.combo_taste.currentIndex(), role_db)
        # цена
        price = int(self.line_price.text().strip())
        # объем
        volume = int(self.line_volume.text().strip())

        if self.record_id is None:
            # добавляем
            query = 'insert into coffee (name, roastingid, tasteid, price, volume, groundid) values(?, ?, ?, ?, ?, ?)'
            result = self.parent().con.execute(query, (name, roastingID, tasteID, price, volume, groundID)).fetchall()
        else:
            # обновляем, надо бы конечно посмотреть что изменилось и обновлять прицельно но ладно не будем возиться
            # и так много времени уже потрачено, мы понимаем как надо делать в идеале
            query = 'update coffee set name=?, roastingid=?, tasteid=?, price=?, volume=?, groundid=? where id=?'
            result = self.parent().con.execute(query,
                (name, roastingID, tasteID, price, volume, groundID, self.record_id)).fetchall()

        self.parent().con.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
