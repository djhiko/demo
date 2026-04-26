import sys
import os

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import (
    SessionMiddleware,
)  # Миддлвэйр для сессий, в данном случае нужен, чтобы избежать перезагрузки страницы после отправки данных с форм, а также для сохранения идентификатора пользователя в контексте запросов

# Конструкция, которая добавляет корень проекта в PYTHON PATH запущенного процесса
sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

from app.database import get_conn
from app.modules.auth import router as auth_router
from app.modules.profile import router as profile_router
from app.modules.admin import router as admin_router

# Корневое приложение FastAPI, необходимое для запуска всего сервиса
app = FastAPI(title="Учитесь.РФ")
app.mount(
    "/static", StaticFiles(directory="app/static")
)  # Монтируем статические файлы в приложение (стили, скрипты и тд)
session_secret = os.getenv("APP_SESSION_SECRET", "dev-secret-change-me")
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
)  # Подключаем миддлвэйр, также для его работы передаем секретный токен (в данном случае можно засунуть любое значение)

# Подключение роутеров сервиса
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(admin_router)

if __name__ == "__main__":
    # Создаем таблицы, описанные в create_tables.sql
    with open("create_tables.sql", "r", encoding="utf-8") as f:
        create_tables_sql_script = f.read()
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(create_tables_sql_script)
    conn.commit()  # Коммитим (сохраняем) внесенные изменения

    # Запуск веб-сервера uvicorn
    uvicorn.run("app.main:app", reload=True)
