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