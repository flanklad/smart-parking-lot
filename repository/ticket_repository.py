import logging
from datetime import datetime
from repository.db import get_connection
from models.ticket import Ticket
from models.slot import ParkingSlot
from models.vehicle import Vehicle
from models.enums import VehicleType
from models.parking_lot import ParkingLot

logger = logging.getLogger(__name__)


class TicketRepository:
      def __init__(self):
          self.conn = get_connection()

      def save_ticket(self, ticket: Ticket):
          self.conn.execute("""
              INSERT INTO tickets(ticket_id, vehicle_no, vehicle_type, slot_id, entry_time, exit_time, fees,lot_id)
              VALUES (?, ?, ?, ?, ?, ?, ?,?)
          """, (
              ticket.ticket_id,
              ticket.vehicle.vehicle_no,
              ticket.vehicle.vehicle_type.value,
              ticket.slot.slot_id,
              ticket.entry_time.strftime('%Y-%m-%d %H:%M:%S'),
              None,
              None,
              ticket.slot.lot_id
          ))
          self.conn.commit()
          logger.info("Ticket saved: %s", ticket.ticket_id)

      def update_ticket(self, ticket: Ticket):
          self.conn.execute("""
              UPDATE tickets SET exit_time = ?, fees = ? WHERE ticket_id = ?
          """, (
              ticket.exit_time.strftime('%Y-%m-%d %H:%M:%S'),
              ticket.fees,
              ticket.ticket_id
          ))
          self.conn.commit()
          logger.info("Ticket updated: %s exit_time=%s", ticket.ticket_id, ticket.exit_time)

      def get_active_ticket(self, vehicle_no: str) -> Ticket | None:
          cursor = self.conn.cursor()
          cursor.execute("""
              SELECT * FROM tickets WHERE vehicle_no = ? AND exit_time IS NULL
          """, (vehicle_no,))
          row = cursor.fetchone()
          if row is None:
              return None
          vehicle = Vehicle(
              vehicle_type=VehicleType(row["vehicle_type"]),
              vehicle_no=row["vehicle_no"]
          )
          slot = ParkingSlot(
              slot_id=row["slot_id"],
              slot_type=VehicleType(row["vehicle_type"]),
              lot_id=row["lot_id"]
          )
          return Ticket(
              ticket_id=row["ticket_id"],
              slot=slot,
              vehicle=vehicle,
              entry_time=datetime.fromisoformat(row["entry_time"]),
              fees=row["fees"]
          )
      def get_tickets_by_date(self, date: str,lot_id: str) -> list[Ticket]:
          cursor = self.conn.cursor()
          cursor.execute("""
              SELECT * FROM tickets
              WHERE entry_time BETWEEN ? AND ?
              AND exit_time IS NOT NULL
              AND lot_id=?
          """, (f"{date} 00:00:00", f"{date} 23:59:59",lot_id))
          rows = cursor.fetchall()
          tickets = []
          for row in rows:
              vehicle = Vehicle(
                  vehicle_type=VehicleType(row["vehicle_type"]),
                  vehicle_no=row["vehicle_no"]
              )
              slot = ParkingSlot(
                  slot_id=row["slot_id"],
                  lot_id=row["lot_id"],
                  slot_type=VehicleType(row["vehicle_type"])
              )
              ticket = Ticket(
                  ticket_id=row["ticket_id"],
                  vehicle=vehicle,
                  slot=slot,
                  entry_time=datetime.fromisoformat(row["entry_time"]),
                  exit_time=datetime.fromisoformat(row["exit_time"]),
                  fees=row["fees"]
              )
              tickets.append(ticket)
          logger.debug("Fetched %d tickets for date %s in lot %s", len(tickets), date,lot_id)
          return tickets
