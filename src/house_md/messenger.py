"""Interface for notifying user"""

from enum import Enum
from abc import ABC, abstractmethod


class Severity(Enum):
    EMEREGENCY = 0
    URGENT = 1
    INFO = 2
    DEBUG = 3


class Messenger(ABC):
    """Interface for user notification"""

    def report_problem(self, description: str) -> None:
        self.send_message(Severity.EMEREGENCY, description)

    def report_problem_fixed(self, description: str) -> None:
        self.send_message(Severity.URGENT, description)

    def send_info(self, text: str) -> None:
        self.send_message(Severity.INFO, text)

    def send_debug(self, text: str) -> None:
        self.send_message(Severity.DEBUG, text)

    @abstractmethod
    def send_message(self, severity: Severity, message: str) -> None:
        pass
