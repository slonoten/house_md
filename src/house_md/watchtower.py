"""Class to check if user should be notified about event or conditions"""

from dataclasses import dataclass
from typing import List

from house_md.house_model import HouseState, HousePowerSupply, Room
from house_md.messenger import Messenger


@dataclass
class RoomTempLimit:
    room_id: str
    min_temp: int
    max_temp: int


@dataclass
class NotifierConfig:
    default_min_temp: int
    default_max_temp: int
    room_temp_limits: List[RoomTempLimit]


class Watchtower:
    """Compares two states and sends notification if needed"""

    def __init__(self, messenger: Messenger, min_temp: int) -> None:
        self.messenger = messenger
        self.min_temp = min_temp
        self.prev_state = None

    def check_state(self, state: HouseState) -> None:
        """Checks conditions and sends notifications if needed"""
        self._check_power(state.power_supply)
        self._check_temperature(state.rooms)
        self.prev_state = state

    def _check_power(self, power_state: HousePowerSupply) -> None:
        line_states = power_state.line_states

        def report_problem() -> None:
            if not any(line_states):
                self.messenger.report_problem("There is no input voltage")
            off_lines = ", ".join(i + 1 for i, state in enumerate(line_states) if not state)
            self.messenger.report_problem(f"There is no input voltage on line(s) {off_lines}")

        if not self.prev_state:
            if all(line_states):
                self.messenger.send_info("Input voltage is present on all lines")
            else:
                report_problem()
        else:
            if self.prev_state.power_supply.line_states != line_states:
                if all(line_states):
                    self.messenger.send_info("Input voltage restored")
                else:
                    report_problem()

    def _check_temperature(self, rooms: List[Room]) -> None:
        if self.prev_state:
            id_to_temp = {room.id: room.temperature for room in self.prev_state.rooms}
        else:
            id_to_temp = {room.id: self.min_temp for room in rooms}  # Fake previous state

        for room in rooms:
            current_temp = room.temperature
            prev_temp = id_to_temp[room.id]
            # Check thermal sensor failures
            if prev_temp is None:
                if current_temp is None:
                    continue
                else:
                    self.messenger.report_problem_fixed(
                        f'Thermal sensor in room "{room.id}" restored with {current_temp}° C'
                    )
                    prev_temp = self.min_temp
            else:
                if current_temp is None:
                    self.messenger.report_problem_fixed(
                        f'Error reading thermal sensor in room "{room.id}"'
                    )
                    continue
            # Check if temperature moved over the limit
            if current_temp < self.min_temp and prev_temp >= self.min_temp:
                self.messenger.report_problem(
                    f'Temprature in room "{room.id}" ({current_temp:.2}° C) dropped below the limit'
                    f" ({self.min_temp:.2}° C)"
                )
            elif current_temp >= self.min_temp and prev_temp < self.min_temp:
                self.messenger.report_problem_fixed(
                    f'Temprature in room "{room.id}" ({current_temp:.2}° C) has risen above the'
                    f" limit ({self.min_temp:.2}° C)"
                )
