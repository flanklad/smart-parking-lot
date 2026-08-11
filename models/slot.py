from models.enums import VehicleType,SlotStatus
from models.vehicle import Vehicle
class ParkingSlot:
    def __init__(self,slot_id: str,lot_id:str,slot_type: VehicleType,slot_status:SlotStatus=SlotStatus.AVAILABLE,current_vehicle:Vehicle=None):
        self.slot_id = slot_id
        self.slot_type = slot_type
        self.current_vehicle = current_vehicle
        self.slot_status = slot_status
        self.lot_id=lot_id
