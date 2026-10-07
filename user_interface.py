from abc import ABC, abstractmethod


class UserInterface(ABC):

    @abstractmethod
    def get_input(self):
        raise NotImplementedError


class ConsoleUserInterface(UserInterface):

    def get_input(self):
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        confirm_password = input("Подтвердите пароль: ")
        return login, password, confirm_password