from enum import Enum

class VehicleType(Enum):
    CAR="car"
    BIKE="bike"
    TRUCK="truck"

class SlotStatus(Enum):
    AVAILABLE="AVAILABLE"
    RESERVED="RESERVED"
    OCCUPIED="OCCUPIED"

