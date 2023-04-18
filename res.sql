--
-- Файл сгенерирован с помощью SQLiteStudio v3.3.3 в Вт апр 18 22:33:39 2023
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: db
CREATE TABLE db (Id PRIMARY KEY, RoleId REFERENCES roles);

-- Таблица: roles
CREATE TABLE roles (RoleId INTEGER PRIMARY KEY, Role);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
