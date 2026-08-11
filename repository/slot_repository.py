from models.slot import ParkingSlot
from models.vehicle import VehicleType
from models.enums import SlotStatus
import logging
from repository.db import get_connection

logger=logging.getLogger(__name__)

class SlotRepository:
    def __init__(self):
        self.conn=get_connection()

    def save_slot(self, slot: ParkingSlot,lot_id):
        self.conn.execute("""
            INSERT INTO slots(slot_id,vehicle_no,slot_type,slot_status,lot_id)
            VALUES (?,?,?,?,?)
            """, (slot.slot_id, slot.current_vehicle.vehicle_no if slot.current_vehicle else None, slot.slot_type.value,
                  slot.slot_status.value,lot_id))
        self.conn.commit()


    def update_slot(self, slot: ParkingSlot):
        self.conn.execute("""
        UPDATE slots SET slot_status=?,vehicle_no=? WHERE slot_id=?
        """, (slot.slot_status.value, slot.current_vehicle.vehicle_no if slot.current_vehicle else None, slot.slot_id))
        self.conn.commit()


    def slots_exist(self,lot_id) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM slots WHERE lot_id=?",(lot_id,))
        count = cursor.fetchone()[0]
        logger.debug("Slots in DB: %d", count)
        return count > 0


    def get_available_slot(self, vehicle_type: VehicleType,lot_id) -> ParkingSlot:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM slots WHERE slot_status=? AND slot_type=? AND lot_id=? LIMIT 1
        """, (SlotStatus.AVAILABLE.value, vehicle_type.value,lot_id))
        row = cursor.fetchone()

        if row is None:
           return None
        logger.debug("Available slot found for %s in %s: %s", vehicle_type.value, row["lot_id"],row["slot_id"])
        return ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["slot_type"]),
            slot_status=SlotStatus(row["slot_status"]),
            lot_id=row["lot_id"])

    def get_reserved_slot(self,vehicle_no: str,lot_id) -> ParkingSlot:
        cursor=self.conn.cursor()
        cursor.execute('''
        SELECT * FROM slots WHERE slot_status=? AND vehicle_no=? AND lot_id=? LIMIT 1
        ''',(SlotStatus.RESERVED.value, vehicle_no,lot_id))
        row= cursor.fetchone()
        if row is None:
            return None
        logger.debug("Reserved slot found: %s", row["slot_id"])
        return ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["slot_type"]),
            slot_status=SlotStatus(row["slot_status"]),
            lot_id=row["lot_id"]
        )

    def get_slot(self, slot_id):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM slots WHERE slot_id=?
        """, (slot_id,))
        row = cursor.fetchone()

        if row is None:
            return None
        logger.debug("Slot found: %s", slot_id)
        return ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["slot_type"]),
            slot_status=SlotStatus(row["slot_status"]),
            lot_id=row["lot_id"]
        )
    def is_lot_full(self,lot_id)-> bool:
        cursor=self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM slots WHERE lot_id=? AND slot_status=?
        ''',(lot_id,SlotStatus.AVAILABLE.value))
        count= cursor.fetchone()[0]
        return count == 0
