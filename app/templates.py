from datetime import datetime

from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(
    directory="app/templates"
)  # Объект, необходимый для обращения и отдачи html-страниц в эндпоинтах


def format_date(value):
    """Функция для преобразования даты в человекочитаемый формат"""
    if not value:
        return ""

    return datetime.strptime(value, "%Y-%m-%d").strftime("%d.%m.%Y")


templates.env.filters["format_date"] = format_date
