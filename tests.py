import unittest
from unittest.mock import patch, MagicMock

from calculations import Validator
from database import Database
from user_interface import UserInterface, ConsoleUserInterface
from external_service import EmailService
from controller import Controller


# ---------- Вспомогательная реализация интерфейса для тестов (заглушка) ----------
class FakeUserInterface(UserInterface):
    def __init__(self, data):
        self._data = data

    def get_input(self):
        return self._data


#ЮНИТ-ТЕСТЫ

class TestValidatorUnit(unittest.TestCase):
    """Тест класса вычислений/валидации (изоляция модуля)."""

    def setUp(self):
        self.v = Validator()

    def test_valid_credentials(self):
        result, message = self.v.calculate("user@mail.com", "pass123", "pass123")
        self.assertTrue(result)
        self.assertEqual(message, "Авторизация успешна")

    def test_invalid_login_and_short_password(self):
        result, message = self.v.calculate("bad-login", "abc", "abc")
        self.assertFalse(result)
        self.assertIn("Некорректный логин", message)
        self.assertIn("не менее 6 символов", message)

    def test_password_mismatch(self):
        result, message = self.v.calculate("user@mail.com", "pass123", "pass124")
        self.assertFalse(result)
        self.assertIn("Пароли не совпадают", message)


class TestDatabaseUnit(unittest.TestCase):
    """Тест класса работы с БД (изоляция модуля)."""

    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        self.db.close()

    def test_add_get_delete(self):
        self.db.add_record("u@m.com", "pass123", "pass123", True, "OK")

        rec = self.db.get_record("u@m.com", "pass123", "pass123")
        self.assertIsNotNone(rec)
        self.assertEqual(rec, (1, "OK"))

        self.db.delete_record("u@m.com", "pass123", "pass123")
        self.assertIsNone(self.db.get_record("u@m.com", "pass123", "pass123"))

    def test_get_missing_record(self):
        self.assertIsNone(self.db.get_record("no@mail.com", "x", "x"))


#ИНТЕГРАЦИОННЫЕ ТЕСТЫ

class TestControllerIntegration(unittest.TestCase):
    """Интеграция Controller + Database + Validator + EmailService."""

    def setUp(self):
        self.db = Database(":memory:")
        self.email = EmailService()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=FakeUserInterface(("user@mail.com", "pass123", "pass123")),
            external_service=self.email,
        )

    def tearDown(self):
        self.db.close()

    def test_new_record_full_scenario(self):
        """Нет записи в БД -> вычисляем -> сохраняем -> отправляем."""
        result, message = self.controller.execute()

        self.assertTrue(result)
        self.assertEqual(message, "Авторизация успешна")

        stored = self.db.get_record("user@mail.com", "pass123", "pass123")
        self.assertEqual(stored, (1, "Авторизация успешна"))

        self.assertEqual(self.email.sent, ["Авторизация успешна"])

    def test_existing_record_uses_db(self):
        """Запись уже есть в БД -> результат берётся из БД, валидатор не вызывается."""
        self.db.add_record("user@mail.com", "pass123", "pass123", True, "Готово из БД")

        validator_mock = MagicMock()
        self.controller.validator = validator_mock

        result, message = self.controller.execute()

        self.assertTrue(result)
        self.assertEqual(message, "Готово из БД")
        validator_mock.calculate.assert_not_called()
        self.assertEqual(self.email.sent, ["Готово из БД"])


class TestConsoleIntegration(unittest.TestCase):
    """Интеграция ConsoleUserInterface + Controller + Database + EmailService."""

    def setUp(self):
        self.db = Database(":memory:")
        self.email = EmailService()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=ConsoleUserInterface(),
            external_service=self.email,
        )

    def tearDown(self):
        self.db.close()

    @patch("builtins.input", side_effect=["user@mail.com", "pass123", "pass123"])
    def test_console_input_success_flow(self, mock_input):
        result, message = self.controller.execute()

        self.assertTrue(result)
        self.assertEqual(message, "Авторизация успешна")
        self.assertEqual(mock_input.call_count, 3)
        self.assertEqual(len(self.email.sent), 1)

    @patch("builtins.input", side_effect=["user@mail.com", "abc", "xyz"])
    def test_console_input_invalid_flow(self, mock_input):
        result, message = self.controller.execute()

        self.assertFalse(result)
        self.assertIn("Пароли не совпадают", message)
        # запись об ошибке всё равно сохранена в БД
        stored = self.db.get_record("user@mail.com", "abc", "xyz")
        self.assertIsNotNone(stored)
        self.assertEqual(stored[0], 0)


class TestExternalServiceIntegration(unittest.TestCase):
    """Интеграция Controller + внешняя зависимость (заглушка)."""

    def setUp(self):
        self.db = Database(":memory:")
        self.external_mock = MagicMock()
        self.controller = Controller(
            validator=Validator(),
            database=self.db,
            user_interface=FakeUserInterface(("user@mail.com", "pass123", "pass123")),
            external_service=self.external_mock,
        )

    def tearDown(self):
        self.db.close()

    def test_external_service_called_with_message(self):
        self.controller.execute()

        self.external_mock.send.assert_called_once_with("Авторизация успешна")


if __name__ == "__main__":
    unittest.main(verbosity=2)