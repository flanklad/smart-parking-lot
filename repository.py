import os
import sqlite3
from models import Vehicle, ParkingSlot, SlotStatus, Ticket, VehicleType
from datetime import datetime

import logging
logger=logging.getLogger(__name__)

class ParkingRepository:
    def __init__(self,db_path:str):
        #print(f"DB location: {os.path.abspath(db_path)}")
        self.conn = sqlite3.connect("parking.db")
        self.conn.row_factory=sqlite3.Row
        self.create_tables()

    def create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS slots(
             slot_id TEXT PRIMARY KEY,
             slot_type TEXT NOT NULL,
             slot_status TEXT NOT NULL,
             vehicle_no TEXT 
            
             )
        """)
        self.conn.commit()
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets(
             ticket_id TEXT PRIMARY KEY,
             slot_id TEXT NOT NULL,
             vehicle_no TEXT NOT NULL,
             vehicle_type TEXT NOT NULL,
             entry_time DATETIME NOT NULL,
             exit_time DATETIME,
             fees REAL 
             )
        """)
        self.conn.commit()

    def save_slot(self,slot:ParkingSlot):
        self.conn.execute("""
            INSERT INTO slots(slot_id,vehicle_no,slot_type,slot_status)
            VALUES (?,?,?,?)
            """,(slot.slot_id,slot.current_vehicle.vehicle_no if slot.current_vehicle else None ,slot.slot_type.value,slot.slot_status.value))
        self.conn.commit()

    def update_slot(self,slot:ParkingSlot):
        self.conn.execute("""
        UPDATE slots SET slot_status=?,vehicle_no=? WHERE slot_id=?
        """,(slot.slot_status.value,slot.current_vehicle.vehicle_no if slot.current_vehicle else None ,slot.slot_id))
        self.conn.commit()

    def slots_exist(self) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM slots")
        count = cursor.fetchone()[0]
        logger.debug("Slots in DB: %d", count)
        return count > 0

    def get_available_slot(self,vehicle_type:VehicleType):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM slots WHERE slot_status=? AND slot_type=? LIMIT 1
        """,(SlotStatus.AVAILABLE.value,vehicle_type.value))
        row=cursor.fetchone()

        if row is None:
            return None
        logger.debug("Available slot found for %s: %s", vehicle_type.value, row["slot_id"])
        return ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["slot_type"]),
            slot_status=SlotStatus(row["slot_status"]))

    def get_slot(self,slot_id):
        cursor=self.conn.cursor()
        cursor.execute("""
        SELECT * FROM slots WHERE slot_id=?
        """,(slot_id,))
        row=cursor.fetchone()

        if row is None:
            return None
        logger.debug("Slot found: %s", slot_id)
        return ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["slot_type"]),
            slot_status=SlotStatus(row["slot_status"])
        )

    def save_ticket(self,ticket:Ticket):
        self.conn.execute("""
        INSERT INTO tickets(ticket_id,vehicle_no,vehicle_type,slot_id,entry_time,exit_time,fees)
        VALUES(?,?,?,?,?,?,?)
        """,(ticket.ticket_id,ticket.vehicle.vehicle_no,ticket.vehicle.vehicle_type.value,ticket.slot.slot_id,ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S'),None,None))
        self.conn.commit()
        logger.info("Ticket saved: %s", ticket.ticket_id)

    def update_ticket(self,ticket:Ticket):
        self.conn.execute("""
        UPDATE tickets SET exit_time=?,fees=? WHERE ticket_id=?
        """,(ticket.exit_time.strftime('%Y-%m-%d %H:%M:%S'),ticket.fees,ticket.ticket_id))
        self.conn.commit()
        logger.info("Ticket updated: %s, exit_time: %s", ticket.ticket_id, ticket.exit_time)

    def get_active_ticket(self,vehicle_no:str):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM tickets WHERE vehicle_no=? AND exit_time IS NULL
        """,(vehicle_no,))
        row=cursor.fetchone()
        if row is None:
            return None
        vehicle=Vehicle(
            vehicle_type=VehicleType(row["vehicle_type"]),
            vehicle_no=row["vehicle_no"]
        )
        slot=ParkingSlot(
            slot_id=row["slot_id"],
            slot_type=VehicleType(row["vehicle_type"]),
        )
        return Ticket(
            ticket_id=row["ticket_id"],
            slot=slot,
            vehicle=vehicle,
            entry_time=datetime.fromisoformat(row["entry_time"]),
            fees=row["fees"]
        )

    def get_tickets_by_date(self,date:str):#for daily revenue
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT * FROM tickets WHERE entry_time BETWEEN ? AND ? AND exit_time IS NOT NULL
        """,(f"{date} 00:00:00",f"{date} 23:59:59"))
        rows=cursor.fetchall()

        tickets=[]
        for row in rows:
            vehicle = Vehicle(
                vehicle_type=VehicleType(row["vehicle_type"]),
                vehicle_no=row["vehicle_no"]
            )
            slot = ParkingSlot(
                slot_id=row["slot_id"],
                slot_type=VehicleType(row["vehicle_type"]),
            )
            ticket=Ticket(
                ticket_id=row["ticket_id"],
                vehicle=vehicle,
                slot=slot,
                entry_time=datetime.fromisoformat(row["entry_time"]),
                exit_time=datetime.fromisoformat(row["exit_time"]),
                fees=row["fees"]
            )
            tickets.append(ticket)
        return tickets


