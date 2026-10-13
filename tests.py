import unittest
from unittest.mock import patch, MagicMock

from calculations import Validator
from database import Database
from user_interface import UserInterface, ConsoleUserInterface
from external_service import EmailService
from controller import Controller


# ---------- Заглушка интерфейса (для интеграционных тестов) ----------
class FakeUserInterface(UserInterface):
    def __init__(self, data):
        self._data = data

    def get_input(self):
        return self._data


# ======================== ЮНИТ-ТЕСТЫ ========================

class TestValidatorUnit(unittest.TestCase):
    """Изолированная проверка логики ЛР №1."""

    def setUp(self):
        self.v = Validator()

    def test_valid_email_and_password(self):
        ok, msg = self.v.calculate(
            "user@mail.com", "email", "Пароль1!", "Пароль1!"
        )
        self.assertTrue(ok, msg)
        self.assertEqual(msg, "Регистрация успешна!")

    def test_phone_blacklist(self):
        ok, msg = self.v.validate_login("+7-000-000-0000", "phone")
        # 11 нулей не в блэклисте — значит формат принят, ошибки нет
        self.assertTrue(ok, msg)

        ok, msg = self.v.validate_login("+7-999-123-456", "phone")  # 10 цифр
        self.assertFalse(ok)
        self.assertIn("ровно 11 цифр", msg)

    def test_email_blacklist(self):
        ok, msg = self.v.validate_login("admin@mail.com", "email")
        self.assertFalse(ok)
        self.assertIn("чёрном списке", msg)

    def test_string_login_short(self):
        ok, msg = self.v.validate_login("abc", "string")
        self.assertFalse(ok)
        self.assertIn("минимум 5 символов", msg)

    def test_password_rules(self):
        # слишком короткий
        ok, msg = self.v.validate_password("Па1!")
        self.assertFalse(ok)
        self.assertIn("короткий", msg)

        # нет верхнего регистра
        ok, msg = self.v.validate_password("пароль1!")
        self.assertFalse(ok)
        self.assertIn("верхнем регистре", msg)

        # нет спецсимвола
        ok, msg = self.v.validate_password("Пароль123")
        self.assertFalse(ok)
        self.assertIn("спецсимвол", msg)

        # корректный
        ok, msg = self.v.validate_password("Пароль1!")
        self.assertTrue(ok, msg)

    def test_confirm_mismatch(self):
        ok, msg = self.v.calculate(
            "user@mail.com", "email", "Пароль1!", "Пароль2!"
        )
        self.assertFalse(ok)
        self.assertIn("не совпадают", msg)


class TestDatabaseUnit(unittest.TestCase):
    """Изолированная проверка SQLite-класса."""

    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_get_delete(self):
        self.db.add_record(
            "u@m.com", "Пароль1!", "Пароль1!", "email", True, "OK"
        )
        rec = self.db.get_record("u@m.com", "Пароль1!", "Пароль1!")
        self.assertEqual(rec, (1, "OK", "email"))

        self.db.delete_record("u@m.com", "Пароль1!", "Пароль1!")
        self.assertIsNone(self.db.get_record("u@m.com", "Пароль1!", "Пароль1!"))

    def test_missing_record(self):
        self.assertIsNone(self.db.get_record("no@mail.com", "x", "x"))


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================

class TestControllerIntegration(unittest.TestCase):
    """Controller + Database + Validator + EmailService."""

    def setUp(self):
        self.db = Database(":memory:")
        self.email = EmailService()
        self.logger = MagicMock()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=FakeUserInterface(
                ("email", "user@mail.com", "Пароль1!", "Пароль1!")
            ),
            external_service=self.email,
            logger=self.logger,
        )

    def tearDown(self):
        self.db.close()

    def test_new_record_full_scenario(self):
        """Нет записи -> валидация -> сохранение в БД -> отправка -> лог."""
        result, message = self.controller.execute()

        self.assertTrue(result)
        self.assertEqual(message, "Регистрация успешна!")

        stored = self.db.get_record("user@mail.com", "Пароль1!", "Пароль1!")
        self.assertEqual(stored, (1, "Регистрация успешна!", "email"))

        self.assertEqual(self.email.sent, ["Регистрация успешна!"])
        self.logger.info.assert_called_once()

    def test_existing_record_uses_db(self):
        """Запись уже есть -> валидатор не вызывается."""
        self.db.add_record(
            "user@mail.com", "Пароль1!", "Пароль1!",
            "email", False, "Сообщение из БД"
        )

        validator_mock = MagicMock()
        self.controller.validator = validator_mock

        result, message = self.controller.execute()

        self.assertFalse(result)
        self.assertEqual(message, "Сообщение из БД")
        validator_mock.calculate.assert_not_called()
        self.assertEqual(self.email.sent, ["Сообщение из БД"])
        self.logger.warning.assert_called_once()

    def test_invalid_data_is_stored_and_sent(self):
        """Невалидные данные -> результат False -> запись сохраняется, ошибка уходит наружу."""
        self.controller.user_interface = FakeUserInterface(
            ("email", "admin@mail.com", "Пароль1!", "Пароль1!")
        )
        result, message = self.controller.execute()

        self.assertFalse(result)
        self.assertIn("чёрном списке", message)

        stored = self.db.get_record("admin@mail.com", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(stored)
        self.assertEqual(stored[0], 0)
        self.assertEqual(self.email.sent, [message])


class TestConsoleIntegration(unittest.TestCase):
    """ConsoleUserInterface + Controller + Database + EmailService."""

    def setUp(self):
        self.db = Database(":memory:")
        self.email = EmailService()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=ConsoleUserInterface(),
            external_service=self.email,
            logger=MagicMock(),
        )

    def tearDown(self):
        self.db.close()

    @patch("builtins.input", side_effect=[
        "2", "user@mail.com", "Пароль1!", "Пароль1!"
    ])
    def test_console_email_success(self, mock_input):
        result, message = self.controller.execute()

        self.assertTrue(result)
        self.assertEqual(message, "Регистрация успешна!")
        self.assertEqual(mock_input.call_count, 4)
        self.assertEqual(len(self.email.sent), 1)

    @patch("builtins.input", side_effect=[
        "1", "+7-999-123-4567", "Пароль1!", "Пароль2!"
    ])
    def test_console_confirm_mismatch(self, mock_input):
        result, message = self.controller.execute()

        self.assertFalse(result)
        self.assertIn("не совпадают", message)
        # запись об ошибке сохраняется в БД
        stored = self.db.get_record("+7-999-123-4567", "Пароль1!", "Пароль2!")
        self.assertIsNotNone(stored)
        self.assertEqual(stored[0], 0)

    @patch("builtins.input", side_effect=["9"])
    def test_console_bad_choice_raises(self, mock_input):
        with self.assertRaises(ValueError):
            self.controller.execute()


class TestExternalServiceIntegration(unittest.TestCase):
    """Controller + внешняя зависимость (заглушка)."""

    def setUp(self):
        self.db = Database(":memory:")
        self.external_mock = MagicMock()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=FakeUserInterface(
                ("string", "alex_user_1", "Пароль1!", "Пароль1!")
            ),
            external_service=self.external_mock,
            logger=MagicMock(),
        )

    def tearDown(self):
        self.db.close()

    def test_external_service_called_with_message(self):
        self.controller.execute()
        self.external_mock.send.assert_called_once_with("Регистрация успешна!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
