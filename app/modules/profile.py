from fastapi import APIRouter, Request, status, Form
from fastapi.responses import RedirectResponse

from app.database import get_conn
from app.templates import templates

router = APIRouter(prefix="/profile")


@router.get("")
def profile_page(request: Request):
    """Эндпоинт для получения профиля текущего пользователя"""
    user_id = request.session.get("user_id")

    if not user_id:
        # Если идентификатора пользователя в контексте сессии нет, то перенаправляем пользователя на страницу аутентификации
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    conn = get_conn()
    cur = conn.cursor()

    # Получаем все заявки пользователя JOIN'я каждый курс для заявки
    requests_rows = cur.execute(
        """
        SELECT
            requests.*,
            courses.name AS course_name,
            courses.description AS course_description
        FROM requests
        JOIN courses ON courses.id = requests.course_id
        WHERE requests.user_id = ?
        """,
        (int(user_id),),
    ).fetchall()

    requests = []

    for row in requests_rows:
        request_dict = dict(row)
        request_dict["can_set_review"] = request_dict["status"] == "Обучение завершено"
        requests.append(request_dict)

    # Получаем все курсы, чтобы пользователь мог выбрать курс при создании заявки
    courses = cur.execute("SELECT * FROM courses").fetchall()

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "requests": requests,
            "courses": courses,
        },
    )


@router.post("/requests")
def create_request(
    request: Request,
    course_id: int = Form(),
    learning_start: str = Form(),
    payment_type: str = Form(),
):
    """Эндпоинт для создания новой заявки пользователя на курс"""
    user_id = request.session.get("user_id")

    if not user_id:
        # Если пользователь не авторизован, то перенаправляем его на страницу входа
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    conn = get_conn()
    cur = conn.cursor()

    # Добавляем новую заявку пользователя в базу данных
    cur.execute(
        """
        INSERT INTO requests (
            user_id,
            course_id,
            status,
            learning_start,
            payment_type
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            int(user_id),
            course_id,
            "Новая",
            learning_start,
            payment_type,
        ),
    )

    conn.commit()

    # После создания заявки возвращаем пользователя обратно в личный кабинет
    return RedirectResponse(
        "/profile",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/requests/{request_id}/reviews")
def create_review(
    request: Request,
    request_id: int,
    review_text: str = Form(),
):
    """Эндпоинт для создания отзыва пользователя по завершенному обучению"""
    user_id = request.session.get("user_id")

    if not user_id:
        # Если пользователь не авторизован, то перенаправляем его на страницу входа
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    conn = get_conn()
    cur = conn.cursor()

    # Получаем заявку пользователя, чтобы проверить возможность оставить отзыв
    user_request = cur.execute(
        """
        SELECT * FROM requests
        WHERE id = ? AND user_id = ?
        """,
        (request_id, int(user_id)),
    ).fetchone()

    if not user_request or user_request["status"] != "Обучение завершено":
        # Если заявка не найдена или обучение еще не завершено, возвращаем пользователя в профиль
        return RedirectResponse(
            "/profile",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Создаем отзыв для курса, указанного в заявке пользователя
    cur.execute(
        """
        INSERT INTO reviews (
            course_id,
            user_id,
            review_text
        )
        VALUES (?, ?, ?)
        """,
        (
            user_request["course_id"],
            int(user_id),
            review_text,
        ),
    )

    conn.commit()

    # После создания отзыва возвращаем пользователя обратно в личный кабинет
    return RedirectResponse(
        "/profile",
        status_code=status.HTTP_303_SEE_OTHER,
    )
