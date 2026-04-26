CREATE TABLE IF NOT EXISTS users ( -- Таблица пользователей
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор пользователя
    login VARCHAR(255) NOT NULL UNIQUE, -- Уникальный логин пользователя для входа в систему
    password TEXT NOT NULL, -- Пароль пользователя для входа в систему
    first_name VARCHAR(255) NOT NULL, -- Имя пользователя
    last_name VARCHAR(255) NOT NULL, -- Фамилия пользователя
    patronymic VARCHAR(255) NOT NULL, -- Отчество пользователя
    phone_number VARCHAR(20) NOT NULL, -- Номер телефона пользователя
    email VARCHAR(255) NOT NULL UNIQUE, -- Email пользователя
    role VARCHAR(20) NOT NULL -- Роль пользователя (admin, user)
);


CREATE TABLE IF NOT EXISTS courses ( -- Таблица курсов
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор курса
    name VARCHAR(255) NOT NULL, -- Название курса
    description TEXT -- Описание курса (опциональное поле)
);

CREATE TABLE IF NOT EXISTS reviews ( -- Таблица отзывов на полученные пользователями услуги
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор отзыва
    course_id INTEGER NOT NULL REFERENCES courses(id), -- Внешний ключ, указывающий на курс, для которого создан отзыв
    user_id INTEGER NOT NULL REFERENCES users(id), -- Внешний ключ, указывающий на пользователя, который оставил отзыв
    review_text TEXT NOT NULL -- Сам текст отзыва, который пользователь оставил 
);

CREATE TABLE IF NOT EXISTS requests ( -- Таблица заявки пользователя на курс
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор заявки
    user_id INTEGER NOT NULL REFERENCES users(id), -- Внешний ключ, указывающий на пользователя, который создал заявку
    course_id INTEGER NOT NULL REFERENCES courses(id), -- Внешний ключ, указывающий на курс, на который была подана заявка
    status VARCHAR(30), -- Статус заявки, допустимые значения: "Новая", "Идет обучение", "Обучение завершено"
    learning_start DATE NOT NULL, -- Предпочтительная дата начала обучения пользователем на курсе
    payment_type VARCHAR(30) NOT NULL -- Предпочтительный вид оплаты пользователем курса. Допустимые значения: "Карта", "Перевод"
);