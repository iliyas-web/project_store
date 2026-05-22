-- database.sql

CREATE DATABASE project_store;

USE project_store;

CREATE TABLE projects(
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255),
    description TEXT,
    tech_stack VARCHAR(255),
    price INT,
    image VARCHAR(255)
);