from models.ticket import Ticket
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

    def select_lot(self,lot_service):
        lots = lot_service.get_all_lots()
        if lots:
            print("\n===EXISTING LOTS===")
            for i, lot in enumerate(lots, 1):
                print(f"{i}. {lot.lot_name} (ID: {lot.lot_id})")
            print(f"{len(lots) + 1}. Create new lot")
            choice = input("Select lot: ")
            if choice.isdigit() and 1 <= int(choice) <= len(lots):
                return lots[int(choice) - 1]

        print("\n===CREATE NEW LOT===")

        try:
            lot_name = input("Lot name: ")
            car_rate = float(input("Car rate per hour: "))
            bike_rate = float(input("Bike rate per hour: "))
            truck_rate = float(input("Truck rate per hour: "))
            car_slots = int(input("Number of car slots: "))
            bike_slots = int(input("Number of bike slots: "))
            truck_slots = int(input("Number of truck slots: "))
        except ValueError:
            print("Invalid input. Please enter integer value.")
            return self.select_lot(lot_service)
        lot = lot_service.create_lot(lot_name, car_rate, bike_rate, truck_rate, car_slots, bike_slots, truck_slots)
        print(f"Lot {lot.lot_name} created successfully.")
        return lot

