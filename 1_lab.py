import re
import logging
import sys
import traceback

# ─── Чёрный список логинов ───
BLACKLIST = {
    "admin", "root", "superuser", "test", "guest",
    "user", "support", "moderator", "administrator", "system"
}

# ─── Настройка логирования ───
logger = logging.getLogger("registration_logger")
logger.setLevel(logging.DEBUG)

if logger.handlers:
    logger.handlers.clear()

file_handler = logging.FileHandler("registration.log", encoding="utf-8")
console_handler = logging.StreamHandler(sys.stdout)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# ─── Регулярные выражения ───
PHONE_PATTERN = re.compile(r'^\+\d-\d{3}-\d{3}-\d{4}$')
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
STRING_LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9_]{5,}$')
PASSWORD_ALLOWED_PATTERN = re.compile(r'^[а-яА-ЯёЁ0-9!@#$%^&*()_+\-={};:\'",.<>/?\\|`~]+$')


def validate_login(login: str, login_type: str) -> tuple[bool, str]:
    """Валидация логина по выбранному типу."""
    if not login or not login.strip():
        return False, "Логин не указан (пустая строка)."

    login = login.strip()

    if login_type == "phone":
        if not PHONE_PATTERN.match(login):
            return False, (
                "Телефон должен быть в формате +x-xxx-xxx-xxxx "
                "(например, +7-999-123-4567)."
            )
        digits_only = re.sub(r'\D', '', login)
        if len(digits_only) != 11:
            return False, f"В номере телефона должно быть ровно 11 цифр, найдено {len(digits_only)}."
        if digits_only in BLACKLIST:
            return False, f"Номер телефона '{login}' находится в чёрном списке."
        return True, ""

    elif login_type == "email":
        if not EMAIL_PATTERN.match(login):
            return False, "Email введён в некорректном формате (например, user@example.com)."
        check_value = login.split('@')[0].lower()
        if check_value in BLACKLIST:
            return False, f"Логин '{login}' находится в чёрном списке и запрещён к регистрации."
        return True, ""

    elif login_type == "string":
        if not STRING_LOGIN_PATTERN.match(login):
            return False, (
                "Логин-строка: минимум 5 символов, только латиница, "
                "цифры и знак подчёркивания."
            )
        if login.lower() in BLACKLIST:
            return False, f"Логин '{login}' находится в чёрном списке и запрещён к регистрации."
        return True, ""

    return False, "Неизвестный тип логина."


def validate_password(password: str) -> tuple[bool, str]:
    """Валидация пароля."""
    if not password or not password.strip():
        return False, "Пароль не указан (пустая строка)."

    password = password.strip()

    if len(password) < 7:
        return False, "Пароль слишком короткий: минимум 7 символов."

    if not PASSWORD_ALLOWED_PATTERN.match(password):
        return False, (
            "Пароль содержит недопустимые символы: разрешены только "
            "кириллица, цифры и спецсимволы."
        )

    if not re.search(r'[А-ЯЁ]', password):
        return False, "В пароле должна быть минимум одна буква в верхнем регистре."

    if not re.search(r'[а-яё]', password):
        return False, "В пароле должна быть минимум одна буква в нижнем регистре."

    if not re.search(r'[0-9]', password):
        return False, "В пароле должна быть минимум одна цифра."

    if not re.search(r'[!@#$%^&*()_+\-={};:\'",.<>/?\\|`~]', password):
        return False, "В пароле должен быть минимум один спецсимвол."

    return True, ""


# ─── Интерактивный ввод с мгновенной проверкой ───
if __name__ == "__main__":
    print("--- Регистрация нового пользователя ---")
    print("Выберите тип логина:")
    print("1 — Телефон (формат +x-xxx-xxx-xxxx)")
    print("2 — Email")
    print("3 — Обычная строка (мин. 5 символов, латиница, цифры, _)")

    choice = input("Введите номер варианта (1/2/3): ").strip()
    login_type = ""
    login = ""

    if choice == "1":
        login_type = "phone"
        login = input("Введите телефон (например, +7-999-123-4567): ").strip()
    elif choice == "2":
        login_type = "email"
        login = input("Введите email (например, user@example.com): ").strip()
    elif choice == "3":
        login_type = "string"
        login = input("Введите логин-строку (например, alex_user_1): ").strip()
    else:
        print("Неверный выбор типа логина. Регистрация прервана.")
        sys.exit(1)

    # ── ШАГ 1: Проверка логина сразу после ввода ──
    ok, msg = validate_login(login, login_type)
    if not ok:
        print(f"\nОШИБКА ЛОГИНА: {msg}")
        logger.warning(
            f"НЕУСПЕШНЫЙ ЗАПРОС | login='{login}', type='{login_type}' | Ошибка: {msg}"
        )
        sys.exit(1)
    else:
        print("Логин корректен.")

    # ── ШАГ 2: Ввод и проверка пароля ──
    password = input("Введите пароль: ")

    ok, msg = validate_password(password)
    if not ok:
        print(f"\nОШИБКА ПАРОЛЯ: {msg}")
        logger.warning(
            f"НЕУСПЕШНЫЙ ЗАПРОС | login='{login}', type='{login_type}', "
            f"password='{password}' | Ошибка: {msg}"
        )
        sys.exit(1)
    else:
        print("Пароль корректен.")

    # ── ШАГ 3: Ввод и проверка подтверждения ──
    confirm = input("Подтвердите пароль: ")

    if password != confirm:
        msg = "Пароль и подтверждение пароля не совпадают."
        print(f"\nОШИБКА: {msg}")
        logger.warning(
            f"НЕУСПЕШНЫЙ ЗАПРОС | login='{login}', type='{login_type}', "
            f"password='{password}', password_confirm='{confirm}' | Ошибка: {msg}"
        )
        sys.exit(1)

    # ── УСПЕХ ──
    print("\nРегистрация успешна!")
    logger.info(
        f"УСПЕШНЫЙ ЗАПРОС | login='{login}', type='{login_type}', "
        f"password='{password}', password_confirm='{confirm}' | Результат: True"
    )
