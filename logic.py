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



