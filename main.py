import sys
import logging

from calculations import Validator
from database import Database
from user_interface import ConsoleUserInterface
from external_service import EmailService
from controller import Controller


def setup_logger():
    logger = logging.getLogger("registration_logger")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        logger.handlers.clear()

    fh = logging.FileHandler("registration.log", encoding="utf-8")
    ch = logging.StreamHandler(sys.stdout)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def main():
    logger = setup_logger()

    controller = Controller(
        validator=Validator(),
        database=Database("app.db"),
        user_interface=ConsoleUserInterface(),
        external_service=EmailService(),
        logger=logger,
    )

    try:
        result, message = controller.execute()
    except ValueError as e:
        print(e)
        return

    print(f"\nРезультат: {result}\nСообщение: {message}")


if __name__ == "__main__":
    main()
