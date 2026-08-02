import sys

from models import ParkingLot, Vehicle, VehicleType
from repository import ParkingRepository
from controller import ParkingController
from view import ParkingView
from exceptions import SlotNotAvailableError, VehicleNotFoundError

import logging
logging.basicConfig(
    force=True,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        logging.FileHandler("parking_logs.log"),
    ]
)
logger=logging.getLogger(__name__)

def main():
    rates = {VehicleType.CAR: 50.0, VehicleType.BIKE: 20.0, VehicleType.TRUCK:
        100.0}
    lot = ParkingLot("Advant-Parking-Lot", rates)
    repo = ParkingRepository("parking.db")
    controller = ParkingController(lot, repo)
    view = ParkingView()

    controller.add_parking_lot(car_slots=15, bike_slots=3, truck_slots=2)
    logger.info("Parking Lot %s initialized",lot.lot_name)

    while True:
            print("\n1. Park Vehicle")
            print("2. Remove Vehicle")
            print("3. Reserve Slot")
            print("4. Daily Revenue")
            print("5. Exit")
            choice = input("Enter choice: ")
            print()

            if choice == "1":
                vehicle_no = input("Enter vehicle number: ")
                while True:
                    vehicle_type = input("Enter vehicle type (car/bike/truck): ")
                    try:
                        vehicle = Vehicle(VehicleType(vehicle_type), vehicle_no)
                        ticket = controller.park_vehicle(vehicle)
                        view.show_ticket(ticket)
                        break
                    except ValueError:
                        print("Invalid Vehicle Type: Please enter the right vehicle type.")
                    except SlotNotAvailableError as e:
                        print(f"Error: {e}")
                        break
            elif choice == "2":
                vehicle_no = input("Enter vehicle number: ")
                try:
                    vehicle = Vehicle(VehicleType.CAR, vehicle_no)
                    ticket = controller.remove_vehicle(vehicle)
                    view.show_bill(ticket)
                except VehicleNotFoundError as e:
                    print(f"Error: {e}")

            elif choice == "3":
                slot_id = input("Enter slot ID to reserve: ")
                try:
                    controller.reserve_slot(slot_id)
                    print(f"Slot {slot_id} reserved successfully.")
                except SlotNotAvailableError as e:
                    print(f"Error: {e}")

            elif choice == "4":
                date = input("Enter date (YYYY-MM-DD): ")
                total, tickets = controller.daily_revenue(date)
                view.show_revenue_report(total, tickets, date)

            elif choice == "5":
                print("Goodbye!")
                break


if __name__ == "__main__":
    main()