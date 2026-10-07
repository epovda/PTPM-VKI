from abc import ABC, abstractmethod


class ExternalService(ABC):

    @abstractmethod
    def send(self, data: str) -> None:
        raise NotImplementedError


class EmailService(ExternalService):
    """Имитация отправки данных на внешний email-сервер."""

    def __init__(self):
        self.sent = []

    def send(self, data: str) -> None:
        self.sent.append(data)
        print(f"[EmailService] Отправлено: {data}")