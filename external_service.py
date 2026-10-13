from abc import ABC, abstractmethod


class ExternalService(ABC):
    """Интерфейс внешней зависимости (например, email-сервер)."""

    @abstractmethod
    def send(self, data: str) -> None:
        raise NotImplementedError


class EmailService(ExternalService):
    """Имитация отправки результата на внешний сервер."""

    def __init__(self):
        self.sent = []

    def send(self, data: str) -> None:
        self.sent.append(data)
        print(f"[EmailService] Отправлено: {data}")
