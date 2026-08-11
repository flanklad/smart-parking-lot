import uuid
import logging
from datetime import datetime
from models.vehicle import Vehicle
from models.ticket import Ticket
from models.enums import SlotStatus, VehicleType
from repository.lot_repository import LotRepository
from repository.slot_repository import SlotRepository
from repository.ticket_repository import TicketRepository
from models.parking_lot import ParkingLot
from custom_errors.exceptions import SlotNotAvailableError, VehicleNotFoundError

logger = logging.getLogger(__name__)


class VehicleService:
      def __init__(self, slot_repo: SlotRepository, ticket_repo: TicketRepository, lot_repo: LotRepository):
          self.slot_repo = slot_repo
          self.ticket_repo = ticket_repo
          self.lot_repo = lot_repo

      def park_vehicle(self, vehicle: Vehicle,lot_id:str) -> Ticket:

              existing = self.ticket_repo.get_active_ticket(vehicle.vehicle_no)
              if existing:
                  logger.warning("Vehicle %s is already parked", vehicle.vehicle_no)
                  raise SlotNotAvailableError("Vehicle already parked")
              slot = self.slot_repo.get_reserved_slot(vehicle.vehicle_no,lot_id)
              if slot is None:
                  slot = self.slot_repo.get_available_slot(vehicle.vehicle_type,lot_id)
              if slot is None:
                  raise SlotNotAvailableError("No Slot Available")

              ticket = Ticket(
                  ticket_id=str(uuid.uuid4()),
                  vehicle=vehicle,
                  slot=slot,
                  entry_time=datetime.now()
              )
              slot.slot_status = SlotStatus.OCCUPIED
              slot.current_vehicle = vehicle
              self.ticket_repo.save_ticket(ticket)
              self.slot_repo.update_slot(slot)
              logger.info("Vehicle %s parked at slot %s", vehicle.vehicle_no, slot.slot_id)
              return ticket

      def remove_vehicle(self, vehicle: Vehicle) -> Ticket:

              ticket = self.ticket_repo.get_active_ticket(vehicle.vehicle_no)
              if ticket is None:
                  raise VehicleNotFoundError("No active ticket found for vehicle")
              ticket.exit_time = datetime.now()
              lot=self.lot_repo.get_lot_by_id(ticket.slot.lot_id)
              ticket.fees = self._calculate_fee(ticket,lot)
              ticket.slot.current_vehicle = None
              ticket.slot.slot_status = SlotStatus.AVAILABLE
              self.ticket_repo.update_ticket(ticket)
              self.slot_repo.update_slot(ticket.slot)

              logger.info("Vehicle %s removed, fees: %.2f", vehicle.vehicle_no, ticket.fees)
              return ticket

      def _calculate_fee(self, ticket: Ticket,lot:ParkingLot) -> float:
          duration = (ticket.exit_time - ticket.entry_time).total_seconds() / 3600
          rates={
                VehicleType.CAR: lot.car_rate,
                VehicleType.BIKE: lot.bike_rate,
                VehicleType.TRUCK: lot.truck_rate
          }
          rate=rates[ticket.vehicle.vehicle_type]
          return rate * duration

