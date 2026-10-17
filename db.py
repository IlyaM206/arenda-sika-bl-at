from decimal import Decimal
from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/scooter?charset=utf8mb4"
engine = create_engine(DATABASE_URL)


def rows(sql, p=None):
    with engine.connect() as c:
        return [dict(r) for r in c.execute(text(sql), p or {}).mappings()]


def one(sql, p=None):
    r = rows(sql, p)
    return r[0] if r else None


def write(sql, p=None):
    with engine.begin() as c:
        c.execute(text(sql), p or {})


def login(username, password):
    return one(
        "SELECT id, username, full_name, role FROM users WHERE username=:u AND password=:p",
        {"u": username.strip(), "p": password}
    )


def scooters(free=False):
    sql = "SELECT id, serial_number, model, battery_level, status FROM scooters"
    if free:
        sql += " WHERE status='available'"
    return rows(sql + " ORDER BY id")


def tariffs():
    return rows(
        "SELECT id, name, price_per_minute, unlock_fee FROM tariffs "
        "WHERE is_active=1 ORDER BY id"
    )


