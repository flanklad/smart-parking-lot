from models.slot import ParkingSlot
from models.vehicle import Vehicle
from datetime import datetime

class Ticket:
    def __init__(self,ticket_id:str,entry_time:datetime,exit_time:datetime=None,slot:ParkingSlot=None,fees:float=None,vehicle:Vehicle=None):
        self.ticket_id = ticket_id
        self.entry_time = entry_time
        self.exit_time = exit_time
        self.slot=slot # HAS A RELATIONSHIP
        self.fees=fees
        self.vehicle=vehicle
    @property
    def is_closed(self):
        return self.exit_time is not None