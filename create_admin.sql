-- Скрипт для обязательного создания администратора по ТЗ
-- Требование: логин Admin26, пароль Demo20

INSERT INTO users (
    login,
    password,
    first_name,
    last_name,
    patronymic,
    phone_number,
    email,
    role
)
VALUES (
    'Admin26',
    'Demo20',
    'Иван',
    'Иванов',
    'Иванович',
    '+70000000000',
    'admin26@example.com',
    'admin'
)

