import logging
import uuid

from models.enums import VehicleType
from models.parking_lot import ParkingLot
from models.slot import ParkingSlot
from repository import lot_repository
from repository.lot_repository import LotRepository
from repository.ticket_repository import TicketRepository
from repository.slot_repository import SlotRepository

logger = logging.getLogger(__name__)
class LotService:
    def __init__(self, ticket_repo: TicketRepository, lot_repo: LotRepository, slot_repo: SlotRepository):
        self.ticket_repo = ticket_repo
        self.lot_repo = lot_repo
        self.slot_repo = slot_repo

    def daily_revenue(self, date: str,lot_id:str) -> tuple[float, list]:
        tickets = self.ticket_repo.get_tickets_by_date(date,lot_id)
        total = sum(ticket.fees or 0 for ticket in tickets)
        logger.info("Daily revenue for %s: %.2f", date, total)
        return total, tickets

    def create_lot(self,lot_name:str, car_rate: float,bike_rate: float, truck_rate: float,car_slots: int,bike_slots: int,truck_slots:int):
        lot_id = str(uuid.uuid4())

        lot=ParkingLot(
            lot_id=lot_id,
            lot_name=lot_name,
            car_rate=car_rate,
            bike_rate=bike_rate,
            truck_rate=truck_rate
        )
        self.lot_repo.save_lot(lot)

        for i in range(car_slots):
            slot=ParkingSlot(f"C{i+1}_{lot_id[:4]}",lot_id,VehicleType.CAR)
            self.slot_repo.save_slot(slot,lot_id)
        for i in range(bike_slots):
            slot=ParkingSlot(f"B{i+1}_{lot_id[:4]}",lot_id,VehicleType.BIKE)
            self.slot_repo.save_slot(slot,lot_id)
        for i in range(truck_slots):
            slot=ParkingSlot(f"T{i+1}_{lot_id[:4]}",lot_id,VehicleType.TRUCK)
            self.slot_repo.save_slot(slot,lot_id)

        logger.info("Created lot: %s with %d car, %d bike and %d truck slots", lot_id,car_slots,bike_slots,truck_slots)
        return lot

    def get_all_lots(self) -> list:
        return self.lot_repo.get_all_lots()

