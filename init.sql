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