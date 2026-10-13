from abc import ABC, abstractmethod


class UserInterface(ABC):
    """Абстрактный интерфейс получения данных от пользователя."""

    @abstractmethod
    def get_input(self):
        """Возвращает (login_type, login, password, confirm_password)."""
        raise NotImplementedError


class ConsoleUserInterface(UserInterface):
    """Консольный ввод — меню и подсказки как в ЛР №1."""

    def get_input(self):
        print("--- Регистрация нового пользователя ---")
        print("Выберите тип логина:")
        print("1 — Телефон (формат +x-xxx-xxx-xxxx)")
        print("2 — Email")
        print("3 — Обычная строка (мин. 5 символов, латиница, цифры, _)")

        choice = input("Введите номер варианта (1/2/3): ").strip()

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
            raise ValueError("Неверный выбор типа логина. Регистрация прервана.")

        password = input("Введите пароль: ")
        confirm_password = input("Подтвердите пароль: ")

        return login_type, login, password, confirm_password
