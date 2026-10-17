from sqlalchemy import create_engine, text

DATABASE_URL = "mysqlpymysql://root:password@127.0.0.1:3306/scooter_rental?charset=utf8mb4"
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)


def test_connection():
    """Проверк соединние с БД"""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def fetch_all(sql, params=None):
    """Выборка возращающая словари"""
    with engine.connect() as connection:
        result = connection.execute(text(sql), params or {})
    return [dict(row) for row in result.mappings().all()]


def fetch_one(sql, params=None):
    """Выполнить SELECT и вернуть одну запись или None."""
    with engine.connect() as connection:
        row = connection.execute(
            text(sql), params or {}).mappings().first()
    return dict(row) if row else None


def authenticate(username, password):
    """Проверка логин и пароол"""
    return fetch_one(
        "SELECT id, username, full_name, role FROM users "
        "WHERE username = :username AND password = :password",
        {"username": username.strip(), "password": password},
    )


def get_available_scooters():
    return fetch_all(
        "SELECT id, serial_number, model, battery_level, status "
        "FROM scooters WHERE status = 'available' ORDER BY id"
    )


def execute_write(sql, params=None):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            result = connection.execute(text(sql), params or {})
            transaction.commit()
            return result.rowcount
        except Exception:
            transaction.rollback()
        raise
