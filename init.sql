CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    role ENUM('user', 'manager') NOT NULL DEFAULT 'user',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE scooters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    model VARCHAR(100) NOT NULL,
    battery_level TINYINT UNSIGNED NOT NULL DEFAULT 100,
    status ENUM('available', 'rented', 'maintenance') NOT NULL DEFAULT 'available',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_scooter_battery CHECK (battery_level BETWEEN 0 AND 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE tariffs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,
    price_per_minute DECIMAL(10, 2) NOT NULL,
    unlock_fee DECIMAL(10, 2) NOT NULL DEFAULT 0,
    description VARCHAR(255) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_tariff_price CHECK (price_per_minute >= 0),
    CONSTRAINT chk_tariff_unlock CHECK (unlock_fee >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scooter_id INT NOT NULL,
    tariff_id INT NOT NULL,
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME NULL,
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    status ENUM('active', 'completed') NOT NULL DEFAULT 'active',
    CONSTRAINT fk_rentals_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_rentals_scooter FOREIGN KEY (scooter_id) REFERENCES scooters(id) ON DELETE RESTRICT,
    CONSTRAINT fk_rentals_tariff FOREIGN KEY (tariff_id) REFERENCES tariffs(id) ON DELETE RESTRICT,
    INDEX idx_rentals_user_status (user_id, status),
    INDEX idx_rentals_scooter_status (scooter_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

+INSERT INTO users (id, username, password, full_name, role) VALUES
+(1, 'manager', 'manager123', 'Иван Менеджеров', 'manager'),
+(2, 'user1', 'user123', 'Алексей Смирнов', 'user'),
+(3, 'user2', 'user123', 'Мария Иванова', 'user'),
+(4, 'user3', 'user123', 'Дмитрий Петров', 'user');
+
+INSERT INTO scooters (id, serial_number, model, battery_level, status) VALUES
+(1, 'SC-1001', 'Xiaomi Scooter 4', 96, 'available'),
+(2, 'SC-1002', 'Ninebot Max G30', 82, 'rented'),
+(3, 'SC-1003', 'Kugoo S3 Pro', 74, 'available'),
+(4, 'SC-1004', 'Xiaomi Mi Electric 3', 15, 'maintenance'),
+(5, 'SC-1005', 'Ninebot F2', 100, 'available');
+
+INSERT INTO tariffs (id, name, price_per_minute, unlock_fee, description, is_active) VALUES
+(1, 'Эконом', 3.00, 15.00, 'Недорогие короткие поездки', TRUE),
+(2, 'Стандарт', 5.00, 20.00, 'Обычный тариф по минутам', TRUE),
+(3, 'Комфорт', 7.50, 10.00, 'Повышенная ставка за минуту', TRUE),
+(4, 'Архивный тариф', 2.00, 0.00, 'Не отображается при создании аренды', FALSE);
+
+INSERT INTO rentals (id, user_id, scooter_id, tariff_id, start_time, end_time, total_amount, status) VALUES
+(1, 2, 2, 2, DATE_SUB(NOW(), INTERVAL 15 MINUTE), NULL, 0.00, 'active'),
+(2, 3, 1, 1, DATE_SUB(NOW(), INTERVAL 2 DAY), DATE_SUB(NOW(), INTERVAL 2 DAY) + INTERVAL 24 MINUTE, 87.00, 'completed'),
+(3, 4, 3, 3, DATE_SUB(NOW(), INTERVAL 1 DAY), DATE_SUB(NOW(), INTERVAL 1 DAY) + INTERVAL 18 MINUTE, 145.00, 'completed'),
+(4, 2, 5, 1, DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_SUB(NOW(), INTERVAL 5 HOUR) + INTERVAL 12 MINUTE, 51.00, 'completed');