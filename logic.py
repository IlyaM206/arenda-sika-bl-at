from pathlib import Path
from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QInputDialog
import db

UI = Path(__file__).parent
SCOOTER_FIELDS = ["id", "serial_number", "model", "battery_level", "status"]
SCOOTER_HEADERS = ["ID", "Номер", "Модель", "Заряд %", "Статус"]
RENTAL_FIELDS = ["id", "user_name", "serial_number", "model", "tariff", "start_time", "end_time", "status", "total_amount"]
RENTAL_HEADERS = ["ID", "Пользователь", "Номер", "Модель", "Тариф", "Начало", "Конец", "Статус", "Сумма"]
USER_FIELDS = ["id", "username", "full_name", "role"]


def error(window, message):
    QMessageBox.critical(window, "Ошибка", str(message))


def show_rows(table, data, fields):
    table.setRowCount(len(data))
    for i, row in enumerate(data):
        for j, field in enumerate(fields):
            value = row[field]
            table.setItem(i, j, QTableWidgetItem("—" if value is None else str(value)))


def selected_id(table):
    row = table.currentRow()
    item = table.item(row, 0) if row >= 0 else None
    return int(item.text()) if item else None


def load_table(window, table, function, fields, *args):
    try:
        show_rows(table, function(*args), fields)
    except Exception as e:
        error(window, e)


def run(window, function, *args):
    try:
        function(*args)
        return True
    except Exception as e:
        error(window, e)
        return False


class LoginLogic:
    def __init__(self, window):
        self.window = window
        self.window.loginButton.clicked.connect(self.login)
        self.window.passwordEdit.returnPressed.connect(self.login)
        self.main_window = None
        self.page_logic = None

    def login(self):
        try:
            user = db.login(self.window.usernameEdit.text(), self.window.passwordEdit.text())
            if not user:
                QMessageBox.warning(self.window, "Вход", "Неверный логин или пароль.")
                return

            name = "manager.ui" if user["role"] == "manager" else "user.ui"
            self.main_window = uic.loadUi(str(UI / name))
            if user["role"] == "manager":
                self.page_logic = ManagerLogic(self.main_window)
            else:
                self.page_logic = UserLogic(self.main_window, user)
            self.main_window.setWindowTitle("Аренда — " + user["full_name"])
            self.main_window.show()
            self.window.close()
        except Exception as e:
            error(self.window, e)


class UserLogic:
    def __init__(self, window, user):
        self.window, self.user = window, user
        self.window.freeTable.setHorizontalHeaderLabels(SCOOTER_HEADERS)
        self.window.historyTable.setHorizontalHeaderLabels(RENTAL_HEADERS)
        self.window.freeTable.horizontalHeader().setStretchLastSection(True)
        self.window.historyTable.horizontalHeader().setStretchLastSection(True)
        self.window.refreshFreeButton.clicked.connect(self.refresh)
        self.window.refreshHistoryButton.clicked.connect(self.refresh)
        self.window.rentButton.clicked.connect(self.rent)
        self.window.finishButton.clicked.connect(self.finish)

        try:
            for tariff in db.tariffs():
                title = f"{tariff['name']} — {tariff['price_per_minute']} руб./мин + {tariff['unlock_fee']} руб."
                self.window.tariffCombo.addItem(title, tariff["id"])
        except Exception as e:
            error(self.window, e)
        self.refresh()

    def refresh(self):
        load_table(self.window, self.window.freeTable, db.scooters, SCOOTER_FIELDS, True)
        load_table(self.window, self.window.historyTable, db.rentals, RENTAL_FIELDS, self.user["id"])

    def rent(self):
        scooter_id = selected_id(self.window.freeTable)
        tariff_id = self.window.tariffCombo.currentData()
        if scooter_id is None or tariff_id is None:
            QMessageBox.warning(self.window, "Аренда", "Выберите самокат и тариф.")
            return
        if run(self.window, db.rent, self.user["id"], scooter_id, tariff_id):
            self.refresh()

    def finish(self):
        rental_id = selected_id(self.window.historyTable)
        if rental_id is None:
            QMessageBox.warning(self.window, "Аренда", "Выберите аренду.")
            return
        if run(self.window, db.finish, rental_id, self.user["id"]):
            self.refresh()


class ManagerLogic:
    def __init__(self, window):
        self.window = window
        self.window.scootersTable.setHorizontalHeaderLabels(SCOOTER_HEADERS)
        self.window.rentalsTable.setHorizontalHeaderLabels(RENTAL_HEADERS)
        self.window.usersTable.setHorizontalHeaderLabels(["ID", "Логин", "ФИО", "Роль"])
        for table in (self.window.scootersTable, self.window.rentalsTable, self.window.usersTable):
            table.horizontalHeader().setStretchLastSection(True)

        self.window.refreshScootersButton.clicked.connect(self.refresh)
        self.window.refreshRentalsButton.clicked.connect(self.refresh)
        self.window.refreshUsersButton.clicked.connect(self.refresh)
        self.window.addScooterButton.clicked.connect(self.add_scooter)
        self.window.deleteScooterButton.clicked.connect(self.delete_scooter)
        self.refresh()

    def refresh(self):
        load_table(self.window, self.window.scootersTable, db.scooters, SCOOTER_FIELDS)
        load_table(self.window, self.window.rentalsTable, db.rentals, RENTAL_FIELDS)
        load_table(self.window, self.window.usersTable, db.users, USER_FIELDS)

    def add_scooter(self):
        serial, ok = QInputDialog.getText(self.window, "Новый самокат", "Серийный номер:")
        if not ok or not serial.strip():
            return
        model, ok = QInputDialog.getText(self.window, "Новый самокат", "Модель:")
        if ok and model.strip() and run(self.window, db.add_scooter, serial, model):
            self.refresh()

    def delete_scooter(self):
        scooter_id = selected_id(self.window.scootersTable)
        if scooter_id is None:
            QMessageBox.warning(self.window, "Самокаты", "Выберите самокат.")
            return
        answer = QMessageBox.question(self.window, "Удаление", "Удалить выбранный самокат?")
        if answer == QMessageBox.Yes and run(self.window, db.delete_scooter, scooter_id):
            self.refresh()
