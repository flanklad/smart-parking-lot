from datetime import datetime
import threading
import uuid
from repository import ParkingRepository
from models import ParkingLot,Vehicle,ParkingSlot,Ticket,VehicleType,SlotStatus
from exceptions import SlotNotAvailableError, VehicleNotFoundError

import logging
logger=logging.getLogger(__name__)


class ParkingController:
    def __init__(self,lot:ParkingLot,repo: ParkingRepository):
        self.lot=lot
        self.repo=repo
        self.lock=threading.Lock()

    def add_parking_lot(self,car_slots:int,bike_slots:int,truck_slots:int):
        if self.repo.slots_exist():
            return
        for i in range(car_slots):
            slot=ParkingSlot(f"C{i+1}",VehicleType.CAR)# only 2 coz they have default value
            self.repo.save_slot(slot)
            self.lot.slots.append(slot)
            logger.debug("Slot %s created", slot.slot_id)
        for i in range(bike_slots):
            slot=ParkingSlot(f"B{i+1}",VehicleType.BIKE)
            self.repo.save_slot(slot)
            self.lot.slots.append(slot)
            logger.debug("Slot %s created", slot.slot_id)
        for i in range(truck_slots):
            slot=ParkingSlot(f"T{i+1}",VehicleType.TRUCK)
            self.repo.save_slot(slot)
            self.lot.slots.append(slot)
            logger.debug("Slot %s created", slot.slot_id)


    def park_vehicle(self,vehicle:Vehicle):
       with self.lock:
           existing=self.repo.get_active_ticket(vehicle.vehicle_no)
           if existing:
               logger.warning("Vehicle %s is already parked", vehicle.vehicle_no)
               raise SlotNotAvailableError("Vehicle already parked")
           slot=self.repo.get_available_slot(vehicle.vehicle_type)
           if slot is None:
               raise SlotNotAvailableError("Slot not available")

           ticket= Ticket(
               ticket_id=str(uuid.uuid4()),
               vehicle=vehicle,
               slot=slot,
               entry_time=datetime.now(),
           )
           slot.slot_status=SlotStatus.OCCUPIED
           slot.current_vehicle=vehicle
           self.repo.save_ticket(ticket)
           self.repo.update_slot(slot)
           self.lot.active_tickets[vehicle.vehicle_no]=ticket
           logger.info("Vehicle %s parked at slot %s", vehicle.vehicle_no, slot.slot_id)
       return ticket

    def remove_vehicle(self,vehicle:Vehicle):
        with self.lock:
            ticket=self.repo.get_active_ticket(vehicle.vehicle_no)
            if ticket is None:
                raise VehicleNotFoundError("No Active Ticket found for Vehicle")

            ticket.exit_time=datetime.now()
            ticket.fees=self.generate_bill(ticket)
            ticket.slot.current_vehicle=None
            ticket.slot.slot_status=SlotStatus.AVAILABLE
            self.repo.update_ticket(ticket)
            self.repo.update_slot(ticket.slot)
            self.lot.active_tickets.pop(vehicle.vehicle_no,None)
            self.lot.closed_tickets.append(ticket)
            logger.info("Vehicle %s removed, fees: %.2f", vehicle.vehicle_no, ticket.fees)
        return ticket

    def generate_bill(self,ticket:Ticket):
        duration = (ticket.exit_time-ticket.entry_time).total_seconds()/3600
        rate= self.lot.rates[ticket.vehicle.vehicle_type]
        return round(duration*rate,2)

    def reserve_slot(self,slot_id:str):
        with self.lock:
            slot= self.repo.get_slot(slot_id)
            if slot is None:
                raise SlotNotAvailableError("Slot not available")
            if slot.slot_status != SlotStatus.AVAILABLE:
                raise SlotNotAvailableError("Slot already occupied")
            slot.slot_status=SlotStatus.RESERVED
            self.repo.update_slot(slot)
            logger.info("Slot %s reserved", slot_id)

    def daily_revenue(self,date:str):
        tickets=self.repo.get_tickets_by_date(date)
        total=sum(ticket.fees for ticket in tickets)
        return total,tickets















