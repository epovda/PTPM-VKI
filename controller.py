from calculations import Validator
from database import Database
from user_interface import UserInterface
from external_service import ExternalService


class Controller:
    """Сквозной сценарий: ввод -> БД/вычисление -> отправка -> возврат результата."""

    def __init__(
        self,
        validator: Validator,
        database: Database,
        user_interface: UserInterface,
        external_service: ExternalService,
    ):
        self.validator = validator
        self.database = database
        self.user_interface = user_interface
        self.external_service = external_service

    def execute(self):
        login, password, confirm_password = self.user_interface.get_input()

        record = self.database.get_record(login, password, confirm_password)

        if record is None:
            # Нет записи в БД -> вычисляем и сохраняем
            result, message = self.validator.calculate(login, password, confirm_password)
            self.database.add_record(login, password, confirm_password, result, message)
        else:
            # Запись уже есть -> берём результат из БД
            result = bool(record[0])
            message = record[1]

        # Отправляем строку-результат сторонней зависимости
        self.external_service.send(message)

        return result, message