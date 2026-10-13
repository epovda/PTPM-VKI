import logging

from calculations import Validator
from database import Database
from user_interface import UserInterface
from external_service import ExternalService


class Controller:
    """Сквозной сценарий: ввод -> БД/валидация -> отправка -> логирование -> возврат."""

    def __init__(self,
                 validator: Validator,
                 database: Database,
                 user_interface: UserInterface,
                 external_service: ExternalService,
                 logger: logging.Logger = None):
        self.validator = validator
        self.database = database
        self.user_interface = user_interface
        self.external_service = external_service
        self.logger = logger or logging.getLogger("registration_logger")

    def execute(self):
        login_type, login, password, confirm_password = self.user_interface.get_input()

        record = self.database.get_record(login, password, confirm_password)

        if record is None:
            result, message = self.validator.calculate(
                login, login_type, password, confirm_password
            )
            self.database.add_record(
                login, password, confirm_password,
                login_type, result, message,
            )
        else:
            result, message, _stored_type = record
            result = bool(result)

        # Логирование как в ЛР №1
        log_line = (
            f"login='{login}', type='{login_type}', "
            f"password='{password}', password_confirm='{confirm_password}'"
        )
        if result:
            self.logger.info(f"УСПЕШНЫЙ ЗАПРОС | {log_line} | Результат: True")
        else:
            self.logger.warning(f"НЕУСПЕШНЫЙ ЗАПРОС | {log_line} | Ошибка: {message}")

        self.external_service.send(message)
        return result, message
