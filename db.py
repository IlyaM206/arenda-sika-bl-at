from datetime import datetime
from decimal import Decimal
from math import ceil

from sqlalchemy import create_engine, text

DATABASE_URL = "mysqlpymysql://root:password@127.0.0.1:3306/scooter_rental?charset=utf8mb4"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)


def test_connection():
    """Проверк соединние с БД"""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
