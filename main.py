import logging
from models.vehicle import Vehicle
from models.enums import VehicleType
from repository.slot_repository import SlotRepository
from repository.ticket_repository import TicketRepository
from repository.lot_repository import LotRepository
from services.vehicle_service import VehicleService
from services.slot_service import SlotService
from services.lot_service import LotService
from custom_errors.exceptions import SlotNotAvailableError, VehicleNotFoundError, InvalidVehicleTypeError

logging.basicConfig(
      force=True,
      level=logging.DEBUG,
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
      datefmt="%d-%b-%y %H:%M:%S",
      handlers=[
          logging.FileHandler("parking_logs.log"),
      ]
  )
logger = logging.getLogger(__name__)


def select_lot(lot_service):
    lots = lot_service.get_all_lots()
    if lots:
        print("\n===EXISTING LOTS===")
        for i, lot in enumerate(lots, 1):
            print(f"{i}. {lot.lot_name}")
            choice = input("Select lot (or press Enter to create new): ")
            if choice.isdigit() and 1 <= int(choice) <= len(lots):
                    return lots[int(choice) - 1]
    print("\n===CREATE NEW LOT===")
    try:
        lot_name = input("Lot name: ")
        car_rate = float(input("Car rate/hr: "))
        bike_rate = float(input("Bike rate/hr: "))
        truck_rate = float(input("Truck rate/hr: "))
        car_slots = int(input("Car slots: "))
        bike_slots = int(input("Bike slots: "))
        truck_slots = int(input("Truck slots: "))
    except ValueError:
        print("Invalid input. Please enter integer value.")
        return select_lot(lot_service)
    lot = lot_service.create_lot(lot_name, car_rate, bike_rate, truck_rate, car_slots, bike_slots, truck_slots)
    print(f"Lot {lot.lot_name} created successfully.")
    return lot


def main():
      slot_repo = SlotRepository()
      ticket_repo = TicketRepository()
      lot_repo = LotRepository()

      vehicle_service = VehicleService(slot_repo, ticket_repo, lot_repo)
      slot_service = SlotService(slot_repo)
      lot_service = LotService(ticket_repo, lot_repo,slot_repo)

      lot = select_lot(lot_service)
      logger.info("Operating on lot %s", lot.lot_name)

      while True:
          print(f"\n===  {lot.lot_name} ===")
          print("1. Park Vehicle")
          print("2. Remove Vehicle")
          print("3. Reserve Slot")
          print("4. Daily Revenue")
          print("5. Switch Lot")
          print("6. Exit")
          choice = input("Enter choice: ")
          print()

          if choice == "1":
              vehicle_no = input("Enter vehicle number: ")
              vehicle_type = input("Enter vehicle type (car/bike/truck): ")
              try:
                  vehicle = Vehicle(VehicleType(vehicle_type), vehicle_no)
                  ticket = vehicle_service.park_vehicle(vehicle, lot.lot_id)
                  print("===PARKING TICKET===")
                  print(f"Vehicle No. : {ticket.vehicle.vehicle_no}")
                  print(f"Slot : {ticket.slot.slot_id}")
                  print(f"Entry Time : {ticket.entry_time}")
                  print("====================")
                  logger.info("Ticket shown for vehicle %s", ticket.vehicle.vehicle_no)
              except InvalidVehicleTypeError as e:
                  print(f"Error: {e}")
              except SlotNotAvailableError as e:
                  print(f"Error: {e}")

          elif choice == "2":
              vehicle_no = input("Enter vehicle number: ")
              vehicle_type = input("Enter vehicle type (car/bike/truck): ")
              try:
                  vehicle = Vehicle(VehicleType(vehicle_type), vehicle_no)
                  ticket = vehicle_service.remove_vehicle(vehicle)
                  print("===PARKING BILL===")
                  print(f"Vehicle No. : {ticket.vehicle.vehicle_no}")
                  print(f"Slot : {ticket.slot.slot_id}")
                  print(f"Entry Time : {ticket.entry_time}")
                  print(f"Duration : {(ticket.exit_time - ticket.entry_time).total_seconds() / 3600}")
                  print(f"fees : {ticket.fees}")
                  print("==================")
                  logger.info("Bill shown for vehicle %s, fees: %.2f", ticket.vehicle.vehicle_no, ticket.fees)

              except ValueError:
                  print("Invalid vehicle type. Please enter car, bike or truck.")
              except VehicleNotFoundError as e:
                  print(f"Error: {e}")

          elif choice == "3":
              slot_id = input("Enter slot ID to reserve: ")
              vehicle_no = input("Enter vehicle number: ")
              vehicle_type = input("Enter vehicle type (car/bike/truck): ")
              try:
                  vehicle = Vehicle(VehicleType(vehicle_type), vehicle_no)
                  slot_service.reserve_slot(slot_id, vehicle)
                  print(f"Slot {slot_id} reserved for {vehicle_no} successfully.")
              except ValueError:
                  print("Invalid vehicle type. Please enter car, bike or truck.")
              except SlotNotAvailableError as e:
                  print(f"Error: {e}")

          elif choice == "4":
              date = input("Enter date (YYYY-MM-DD): ")
              total, tickets = lot_service.daily_revenue(date, lot.lot_id)
              print("===DAILY REVENUE REPORT===")
              print(f"Total Revenue : {total}")
              for t in tickets:
                  print(f"  {t.vehicle.vehicle_no} | {t.vehicle.vehicle_type.value} |{t.fees}")
              print(f"Date : {date}")
              with open(f"revenue_report_{date}.csv", 'w') as file:
                  file.write(f"Date: {date}\n")
                  file.write(f"Total Revenue : {total}\n")
                  for t in tickets:
                      file.write(f"{t.vehicle.vehicle_no},{t.vehicle.vehicle_type.value},{t.fees}\n")
              logger.info("Revenue report generated for %s, total: %.2f", date, total)

          elif choice == "5":
              lot = select_lot(lot_service)
              logger.info("Switched to lot %s", lot.lot_name)

          elif choice == "6":
              print("Goodbye!")
              break


if __name__ == "__main__":
      main()