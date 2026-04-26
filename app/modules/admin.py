from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse

from app.database import get_conn
from app.templates import templates

router = APIRouter(prefix="/admin")


@router.get("")
def admin_page(request: Request):
    """Эндпоинт для получения страницы администратора"""
    user_id = request.session.get("user_id")

    if not user_id:
        # Если идентификатора пользователя в контексте сессии нет, то перенаправляем пользователя на страницу аутентификации
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    conn = get_conn()
    cur = conn.cursor()

    # Получаем текущего пользователя, чтобы проверить его роль
    user = cur.execute(
        "SELECT * FROM users WHERE id = ?",
        (int(user_id),),
    ).fetchone()

    if not user or user["role"] != "admin":
        # Если пользователь не найден или не является администратором, то перенаправляем его в личный кабинет
        return RedirectResponse(
            "/profile",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Получаем все заявки пользователей JOIN'я курс и пользователя для отображения полной информации в админ-панели
    requests = cur.execute(
        """
        SELECT
            requests.*,
            courses.name AS course_name,
            users.login AS user_login,
            users.first_name AS user_first_name,
            users.last_name AS user_last_name
        FROM requests
        JOIN courses ON courses.id = requests.course_id
        JOIN users ON users.id = requests.user_id
        ORDER BY requests.id DESC
        """
    ).fetchall()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "requests": requests,
        },
    )


@router.post("/requests/{request_id}/status")
def update_request_status(
    request: Request,
    request_id: int,
    status_value: str = Form(alias="status"),
):
    """Эндпоинт для изменения статуса заявки администратором"""
    user_id = request.session.get("user_id")

    if not user_id:
        # Если пользователь не авторизован, то перенаправляем его на страницу входа
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    conn = get_conn()
    cur = conn.cursor()

    # Получаем текущего пользователя, чтобы проверить, является ли он администратором
    user = cur.execute(
        "SELECT * FROM users WHERE id = ?",
        (int(user_id),),
    ).fetchone()

    if not user or user["role"] != "admin":
        # Если пользователь не является администратором, то запрещаем ему менять статусы заявок
        return RedirectResponse(
            "/profile",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Список допустимых статусов заявки
    allowed_statuses = [
        "Новая",
        "Идет обучение",
        "Обучение завершено",
    ]

    if status_value not in allowed_statuses:
        # Если пришел некорректный статус, то просто возвращаем администратора обратно в админ-панель
        return RedirectResponse(
            "/admin",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Обновляем статус выбранной заявки
    cur.execute(
        """
        UPDATE requests
        SET status = ?
        WHERE id = ?
        """,
        (
            status_value,
            request_id,
        ),
    )

    # Сохраняем изменения в базе данных
    conn.commit()

    # После изменения статуса возвращаем администратора обратно в админ-панель
    return RedirectResponse(
        "/admin",
        status_code=status.HTTP_303_SEE_OTHER,
    )
