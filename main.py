from calculations import Validator
from database import Database
from user_interface import ConsoleUserInterface
from external_service import EmailService
from controller import Controller


def main():
    controller = Controller(
        validator=Validator(),
        database=Database("app.db"),
        user_interface=ConsoleUserInterface(),
        external_service=EmailService(),
    )
    result, message = controller.execute()
    print(f"\nРезультат: {result}\nСообщение: {message}")


if __name__ == "__main__":
    main()