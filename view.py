from datetime import datetime
from models import Ticket
import logging
logger=logging.getLogger(__name__)

class ParkingView:
    def show_ticket(self,ticket:Ticket):
        print("===PARKING TICKET===")
        print(f"Vehicle No. : {ticket.vehicle.vehicle_no}")
        print(f"Slot : {ticket.slot.slot_id}")
        print(f"Entry Time : {ticket.entry_time}")
        print("====================")
        logger.info("Ticket shown for vehicle %s", ticket.vehicle.vehicle_no)

    def show_bill(self,ticket:Ticket):
        print("===PARKING BILL===")
        print(f"Vehicle No. : {ticket.vehicle.vehicle_no}")
        print(f"Slot : {ticket.slot.slot_id}")
        print(f"Entry Time : {ticket.entry_time}")
        print(f"Duration : {(ticket.exit_time - ticket.entry_time).total_seconds() / 3600}")
        print(f"fees : {ticket.fees}")
        print("==================")
        logger.info("Bill shown for vehicle %s, fees: %.2f", ticket.vehicle.vehicle_no, ticket.fees)

    def show_revenue_report(self,total:float,tickets: list,date:str):
        print("===DAILY REVENUE REPORT===")
        print(f"Total Revenue : {total}")
        for ticket in tickets:
            print(f"  {ticket.vehicle.vehicle_no} | {ticket.vehicle.vehicle_type.value} |{ticket.fees}")
        print(f"Date : {date}")

        with open(f"revenue_report_{date}.csv",'w') as file:
            file.write(f"Date: {date}\n")
            file.write(f"Total Revenue : {total}\n")
            for ticket in tickets:
                file.write(f"{ticket.vehicle.vehicle_no},{ticket.vehicle.vehicle_type.value},{ticket.fees}\n")
        logger.info("Revenue report generated for %s, total: %.2f", date, total)
