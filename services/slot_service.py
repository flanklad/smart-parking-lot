import logging
from models.enums import SlotStatus
from models.vehicle import Vehicle
from repository.lot_repository import LotRepository
from repository.slot_repository import SlotRepository
from custom_errors.exceptions import SlotNotAvailableError

logger = logging.getLogger(__name__)


class SlotService:
    def __init__(self, slot_repo: SlotRepository):
        self.slot_repo = slot_repo

    def reserve_slot(self, slot_id: str,vehicle: Vehicle):
        slot = self.slot_repo.get_slot(slot_id)
        if slot is None:
            raise SlotNotAvailableError("Slot not found")
        if slot.slot_status != SlotStatus.AVAILABLE:
            raise SlotNotAvailableError("Slot is not available for reservation")
        if slot.slot_type!=vehicle.vehicle_type:
            raise SlotNotAvailableError(f"Slot id {slot.slot_type} type is not available for reservation for vehicle {vehicle.vehicle_type}")

        slot.slot_status = SlotStatus.RESERVED
        slot.current_vehicle = vehicle
        self.slot_repo.update_slot(slot)
        logger.info("Slot %s reserved for %s", slot_id,vehicle.vehicle_no)

