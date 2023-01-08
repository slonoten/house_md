"""House model interfaces"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HousePowerSupply:
    """House's power supply line"""

    line_states: List[bool]


@dataclass
class Heater:
    """Remotely controlled heater with on/off state"""

    id: str
    is_on: bool


@dataclass
class Room:
    """Room equipment model"""

    id: str
    temperature: Optional[float] = None
    heaters: List[Heater] | None = None


@dataclass
class HouseState:
    """House model"""

    outside_temperature: float
    power_supply: HousePowerSupply
    rooms: List[Room]
