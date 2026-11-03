from enum import Enum


class MachineStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    DOWN = "down"
    SETUP = "setup"
