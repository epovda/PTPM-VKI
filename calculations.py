import re


class Validator:

    LOGIN_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

    def calculate(self, login: str, password: str, confirm_password: str):
        """
        Возвращает кортеж (result: bool, message: str).
        result == True  -> авторизация успешна
        result == False -> сообщение содержит описание ошибок
        """
        errors = []

        if not login or not self.LOGIN_RE.match(login):
            errors.append("Некорректный логин (ожидается email)")

        if not password or len(password) < 6:
            errors.append("Пароль должен содержать не менее 6 символов")
        elif not re.search(r"\d", password):
            errors.append("Пароль должен содержать хотя бы одну цифру")

        if password != confirm_password:
            errors.append("Пароли не совпадают")

        if errors:
            return False, "; ".join(errors)
        return True, "Авторизация успешна"