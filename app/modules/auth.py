from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse

from app.database import get_conn
from app.templates import templates

router = APIRouter(
    prefix="/auth"
)  # Роутер для модуля аутентификации, prefix - это начало URI, по которому будут доступны все заявленные дальше в модуле пути


@router.get("/register")
def register_page(request: Request):
    """Эндпоинт для отдачи пользователю страницы регистрации"""
    # Забираем и передаем в контекст для отображения ошибки error_message
    error_message = request.session.pop("error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "error_message": error_message,
        },
    )


@router.post("/register")
def register_user(
    request: Request,
    login: str = Form(),
    password: str = Form(),
    last_name: str = Form(),
    first_name: str = Form(),
    patronymic: str = Form(),
    phone_number: str = Form(),
    email: str = Form(),
):
    """Эндпоинт для обработки всех введенных пользователем данных, пришедших с формы регистрации"""
    login = login.strip()
    password = password.strip()
    last_name = last_name.strip()
    first_name = first_name.strip()
    patronymic = patronymic.strip()
    phone_number = phone_number.strip()
    email = email.strip().lower()

    conn = get_conn()
    cur = conn.cursor()

    # Проверяем, существует ли пользователь с таким логином
    existing_user = cur.execute(
        "SELECT id FROM users WHERE login = ?",
        (login,),
    ).fetchone()

    if existing_user:
        # Если пользователь с таким логином уже существует - возвращаем ошибку и редиректим обратно на страницу регистрации
        request.session["error_message"] = "Пользователь с таким логином уже существует"
        return RedirectResponse(
            "/auth/register",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Проверяем, существует ли пользователь с таким email
    existing_email = cur.execute(
        "SELECT id FROM users WHERE email = ?",
        (email,),
    ).fetchone()

    if existing_email:
        # Если пользователь с таким email уже существует - возвращаем ошибку и редиректим обратно на страницу регистрации
        request.session["error_message"] = "Пользователь с таким email уже существует"
        return RedirectResponse(
            "/auth/register",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Добавляем нового пользователя в базу данных
    cur.execute(
        """
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            login,
            password,
            first_name,
            last_name,
            patronymic,
            phone_number,
            email,
            "user",  # По умолчанию при регистрации создается пользователь с ролью user
        ),
    )

    # Сохраняем внесенные изменения в базе данных
    conn.commit()

    # После успешной регистрации перенаправляем пользователя на страницу входа
    return RedirectResponse(
        "/auth/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/login")
def login_page(request: Request):
    """Эндпоинт для отдачи пользователю страницы аутентификации"""
    # Забираем и передаем в контекст для отображения ошибки error_message
    error_message = request.session.pop("error_message", None)

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "error_message": error_message,
        },
    )


@router.post("/login")
def login_user(
    request: Request,
    login: str = Form(),
    password: str = Form(),
):
    """Эндпоинт для обработки логина и пароля пользователя, пришедших с формы аутентификации"""
    login = login.strip()
    password = password.strip()

    conn = get_conn()
    cur = conn.cursor()
    user = cur.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
    if not user or user["password"] != password:
        # Если пользователь не найден в системе, или у него неверный пароль, то возвращаем пользователю ошибку, и редиректим на страницу входа
        request.session["error_message"] = "Неверный логин или пароль"
        return RedirectResponse(
            "/auth/login",
            status_code=status.HTTP_303_SEE_OTHER,  # Статус код, обозначающий получение ответа по другому URL-адресу с помощью GET метода
        )

    # Если пользователь успешно прошел аутентификацию
    request.session["user_id"] = user["id"]
    request.session["role"] = user["role"]

    # Если пользователь является администратором - перенаправляем его в админ-панель
    if user["role"] == "admin":
        return RedirectResponse(
            "/admin",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    # Если пользователь является обычным пользователем - перенаправляем его в личный кабинет
    return RedirectResponse(
        "/profile",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/logout")
def logout_user(request: Request):
    """Эндпоинт для завершения пользовательской сессии"""
    request.session.clear()
    return RedirectResponse(
        "/auth/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )
