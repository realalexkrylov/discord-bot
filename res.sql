--
-- ���� ������������ � ������� SQLiteStudio v3.3.3 � �� ��� 18 22:33:39 2023
--
-- �������������� ��������� ������: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- �������: db
CREATE TABLE db (Id PRIMARY KEY, RoleId REFERENCES roles);

-- �������: roles
CREATE TABLE roles (RoleId INTEGER PRIMARY KEY, Role);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
