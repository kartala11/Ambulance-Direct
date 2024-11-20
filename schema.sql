CREATE DATABASE ambulance_db;

USE ambulance_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    role ENUM('ambulance_driver', 'traffic_police', 'hospital') NOT NULL,
    discord_username VARCHAR(100),
    signal_location VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT
);

CREATE TABLE hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    beds_available INT NOT NULL,
    doctors_available BOOLEAN NOT NULL
);

CREATE TABLE ambulance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    driver_id INT,
    hospital_id INT,
    status ENUM('in_transit', 'arrived') NOT NULL,
    FOREIGN KEY (driver_id) REFERENCES users(id),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id)
);

CREATE TABLE traffic_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    discord_username VARCHAR(100) NOT NULL
);
