import re


class Validator:
    """Валидация логина и пароля — точная логика из ЛР №1."""

    BLACKLIST = {
        "admin", "root", "superuser", "test", "guest",
        "user", "support", "moderator", "administrator", "system",
    }

    PHONE_PATTERN = re.compile(r'^\+\d-\d{3}-\d{3}-\d{4}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    STRING_LOGIN_PATTERN = re.compile(r'^[a-zA-Z0-9_]{5,}$')
    PASSWORD_ALLOWED_PATTERN = re.compile(
        r'^[а-яА-ЯёЁ0-9!@#$%^&*()_+\-={};:\'",.<>/?\\|`~]+$'
    )

    # ---------- Логин ----------
    def validate_login(self, login: str, login_type: str):
        if not login or not login.strip():
            return False, "Логин не указан (пустая строка)."

        login = login.strip()

        if login_type == "phone":
            if not self.PHONE_PATTERN.match(login):
                return False, (
                    "Телефон должен быть в формате +x-xxx-xxx-xxxx "
                    "(например, +7-999-123-4567)."
                )
            digits_only = re.sub(r'\D', '', login)
            if len(digits_only) != 11:
                return False, (
                    f"В номере телефона должно быть ровно 11 цифр, "
                    f"найдено {len(digits_only)}."
                )
            if digits_only in self.BLACKLIST:
                return False, f"Номер телефона '{login}' находится в чёрном списке."
            return True, ""

        if login_type == "email":
            if not self.EMAIL_PATTERN.match(login):
                return False, "Email введён в некорректном формате (например, user@example.com)."
            check_value = login.split('@')[0].lower()
            if check_value in self.BLACKLIST:
                return False, f"Логин '{login}' находится в чёрном списке и запрещён к регистрации."
            return True, ""

        if login_type == "string":
            if not self.STRING_LOGIN_PATTERN.match(login):
                return False, (
                    "Логин-строка: минимум 5 символов, только латиница, "
                    "цифры и знак подчёркивания."
                )
            if login.lower() in self.BLACKLIST:
                return False, f"Логин '{login}' находится в чёрном списке и запрещён к регистрации."
            return True, ""

        return False, "Неизвестный тип логина."

    # ---------- Пароль ----------
    def validate_password(self, password: str):
        if not password or not password.strip():
            return False, "Пароль не указан (пустая строка)."

        password = password.strip()

        if len(password) < 7:
            return False, "Пароль слишком короткий: минимум 7 символов."

        if not self.PASSWORD_ALLOWED_PATTERN.match(password):
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

    # ---------- Сквозная проверка (для контроллера) ----------
    def calculate(self, login: str, login_type: str,
                  password: str, confirm_password: str):
        ok, msg = self.validate_login(login, login_type)
        if not ok:
            return False, msg
        ok, msg = self.validate_password(password)
        if not ok:
            return False, msg
        if password != confirm_password:
            return False, "Пароль и подтверждение пароля не совпадают."
        return True, "Регистрация успешна!"
