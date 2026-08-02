from enum import Enum
from datetime import datetime

class VehicleType(Enum):
    CAR="car"
    BIKE="bike"
    TRUCK="truck"

class SlotStatus(Enum):
    AVAILABLE="AVAILABLE"
    RESERVED="RESERVED"
    OCCUPIED="OCCUPIED"

class Vehicle:
    def __init__(self,vehicle_type: VehicleType, vehicle_no: str):
        self.vehicle_type = vehicle_type
        self.vehicle_no=vehicle_no

class ParkingSlot:
    def __init__(self,slot_id: str,slot_type: VehicleType,slot_status:SlotStatus=SlotStatus.AVAILABLE,current_vehicle:Vehicle=None):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.current_vehicle = current_vehicle
        self.slot_status = slot_status

class Ticket:
    def __init__(self,ticket_id:str,entry_time:datetime,exit_time:datetime=None,slot:ParkingSlot=None,fees:float=None,vehicle:Vehicle=None):
        self.ticket_id = ticket_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.slot=slot
        self.fees=fees
        self.vehicle=vehicle

    @property
    def is_closed(self):
        return self.exit_time is not None

class ParkingLot:
    def __init__(self,lot_name:str,rates:dict[VehicleType,float]):
        self.lot_name = lot_name
        self.slots = []
        self.active_tickets = {}
        self.closed_tickets=[]
        self.rates = rates





