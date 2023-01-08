"""Tests for notifications"""

import re
from typing import List, Tuple

from house_md.house_model import HousePowerSupply, HouseState, Room
from house_md.messenger import Messenger, Severity
from house_md.watchtower import Watchtower


class MessegerMock(Messenger):
    def __init__(self) -> None:
        super().__init__()
        self._messages : List[Tuple[Severity, str]] = []

    def send_message(self, severity: Severity, message: str) -> None:
        self._messages.append((severity, message))

    def find_message(self, pattern: str) -> Tuple[Severity, str] | None:
        for severity, text in self._messages:
            if re.search(pattern, text, re.IGNORECASE):
                return (severity, text)
        return None

    def clear(self) -> None:
        self._messages.clear()

    @property
    def message_count(self) -> int:
        return len(self._messages)


def test_voltage_down_on_start():
    messenger = MessegerMock()
    no_voltage_state = HouseState(0.0, HousePowerSupply([False]), [])  # No voltage
    watchtower = Watchtower(messenger, 3.0)
    watchtower.check_state(no_voltage_state)
    message = messenger.find_message("voltage")
    assert message, "Voltage related message not found"
    severity, _ = message
    assert severity == Severity.FAILURE, "Power failure message should have FAILURE severity"
    
    messenger.clear()
    voltage_restored_state = HouseState(0.0, HousePowerSupply([True]), [])  # Voltage restored 
    watchtower.check_state(voltage_restored_state)
    message = messenger.find_message("voltage")
    assert message, "Voltage related message not found"
    severity, _ = message
    assert severity == Severity.RECOVERY, "Power restore message should have RECOVERY severity"
   
            
def test_voltage_down():
    messenger = MessegerMock()
    voltage_ok_state = HouseState(0.0, HousePowerSupply([True, True, True]), [])  # Voltage ok
    watchtower = Watchtower(messenger, 3.0)
    watchtower.check_state(voltage_ok_state)
    message = messenger.find_message("voltage")
    assert message, "Voltage related message not found"
    severity, _ = message
    assert severity == Severity.INFO, "Power OK message should have INFO severity"

    messenger.clear()
    voltage_down_state = HouseState(0.0, HousePowerSupply([False, True, True]), [])  # No voltage 
    watchtower.check_state(voltage_down_state)
    message = messenger.find_message("voltage")
    assert message, "Voltage related message not found"
    severity, _ = message
    assert severity == Severity.FAILURE, "Power restore message should have FAILURE severity"

    messenger.clear()
    watchtower.check_state(voltage_down_state)
    assert messenger.message_count == 0, "State not changed but messages sent"
