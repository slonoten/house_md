"""Interface for notifying user"""

from enum import Enum
from abc import ABC, abstractmethod


class Severity(Enum):
    FAILURE = 0
    RECOVERY = 1
    INFO = 2
    DEBUG = 3


class Messenger(ABC):
    """Interface for user notification"""

    def report_problem(self, description: str) -> None:
        self.send_message(Severity.FAILURE, description)

    def report_problem_fixed(self, description: str) -> None:
        self.send_message(Severity.RECOVERY, description)

    def send_info(self, text: str) -> None:
        self.send_message(Severity.INFO, text)

    def send_debug(self, text: str) -> None:
        self.send_message(Severity.DEBUG, text)

    @abstractmethod
    def send_message(self, severity: Severity, message: str) -> None:
        pass
