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


def rentals(uid=None):
    sql = "SELECT * FROM rentals"
    p = {}

    if uid is not None:
        sql += " WHERE user_id=:uid"
        p["uid"] = uid

    data = rows(sql + " ORDER BY id DESC", p)

    names = {
        r["id"]: r["full_name"]
        for r in rows("SELECT id, full_name FROM users")
    }
    scooters_data = {
        r["id"]: r for r in rows("SELECT id, serial_number, model FROM scooters")
    }
    tariff_names = {
        r["id"]: r["name"]
        for r in rows("SELECT id, name FROM tariffs")
    }

    result = []

    for r in data:
        s = scooters_data.get(r["scooter_id"], {})

        result.append({
            "id": r["id"],
            "user_name": names.get(r["user_id"], ""),
            "serial_number": s.get("serial_number", ""),
            "model": s.get("model", ""),
            "tariff": tariff_names.get(r["tariff_id"], ""),
            "start_time": r["start_time"],
            "end_time": r["end_time"],
            "status": r["status"],
            "total_amount": r["total_amount"]
        })

    return result


def users():
    return rows("SELECT id, username, full_name, role FROM users ORDER BY id")


def rent(uid, sid, tid):
    with engine.begin() as c:
        s = c.execute(
            text("SELECT status FROM scooters WHERE id=:id FOR UPDATE"),
            {"id": sid}
        ).mappings().first()

        t = c.execute(
            text("SELECT id FROM tariffs WHERE id=:id AND is_active=1"),
            {"id": tid}
        ).first()

        if not s or s["status"] != "available":
            raise ValueError("Самокат недоступен.")

        if not t:
            raise ValueError("Тариф недоступен.")

        c.execute(
            text(
                "INSERT INTO rentals(user_id, scooter_id, tariff_id, status) "
                "VALUES(:u, :s, :t, 'active')"
            ),
            {"u": uid, "s": sid, "t": tid}
        )

        c.execute(
            text("UPDATE scooters SET status='rented' WHERE id=:id"),
            {"id": sid}
        )


def finish(rid, uid):
    with engine.begin() as c:
        r = c.execute(
            text("""
                SELECT scooter_id, tariff_id,
                GREATEST(1, CEIL(TIMESTAMPDIFF(
                    SECOND, start_time, NOW()
                ) / 60)) AS mins
                FROM rentals
                WHERE id=:id AND user_id=:uid AND status='active'
                FOR UPDATE
            """),
            {"id": rid, "uid": uid}
        ).mappings().first()

        if not r:
            raise ValueError("Активная аренда не найдена.")

        t = c.execute(
            text("SELECT price_per_minute, unlock_fee FROM tariffs WHERE id=:id"),
            {"id": r["tariff_id"]}
        ).mappings().first()

        if not t:
            raise ValueError("Тариф не найден.")

        total = (
            Decimal(t["unlock_fee"])
            + Decimal(t["price_per_minute"]) * int(r["mins"])
        ).quantize(Decimal("0.01"))

        c.execute(
            text("""
                UPDATE rentals
                SET status='completed', end_time=NOW(), total_amount=:sum
                WHERE id=:id
            """),
            {"sum": total, "id": rid}
        )

        c.execute(
            text("UPDATE scooters SET status='available' WHERE id=:id"),
            {"id": r["scooter_id"]}
        )


def add_scooter(serial, model):
    write(
        "INSERT INTO scooters(serial_number, model, battery_level, status) "
        "VALUES(:s, :m, 100, 'available')",
        {"s": serial.strip(), "m": model.strip()}
    )


def delete_scooter(sid):
    if one("SELECT id FROM rentals WHERE scooter_id=:id LIMIT 1", {"id": sid}):
        raise ValueError("Нельзя удалить самокат из истории аренд.")

    if not one(
        "SELECT id FROM scooters WHERE id=:id AND status!='rented'",
        {"id": sid}
    ):
        raise ValueError("Самокат не найден или сейчас арендован.")

    write("DELETE FROM scooters WHERE id=:id", {"id": sid})
