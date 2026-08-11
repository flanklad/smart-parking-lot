from models.enums import VehicleType
class Vehicle:
    def __init__(self,vehicle_type: VehicleType, vehicle_no: str):
        self.vehicle_type = vehicle_type
        self.vehicle_no=vehicle_no