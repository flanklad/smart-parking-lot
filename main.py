import logging
from models.vehicle import Vehicle
from models.enums import VehicleType
from repository.slot_repository import SlotRepository
from repository.ticket_repository import TicketRepository
from repository.lot_repository import LotRepository
from services.vehicle_service import VehicleService
from services.slot_service import SlotService
from services.lot_service import LotService
from view import ParkingView
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




def main():
      slot_repo = SlotRepository()
      ticket_repo = TicketRepository()
      lot_repo = LotRepository()

      vehicle_service = VehicleService(slot_repo, ticket_repo, lot_repo)
      slot_service = SlotService(slot_repo)
      lot_service = LotService(ticket_repo, lot_repo,slot_repo)
      view = ParkingView()

      lot = view.select_lot(lot_service)
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
                  view.show_ticket(ticket)
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
                  view.show_bill(ticket)
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
              view.show_revenue_report(total, tickets, date)

          elif choice == "5":
              lot = view.select_lot(lot_service)
              logger.info("Switched to lot %s", lot.lot_name)

          elif choice == "6":
              print("Goodbye!")
              break


if __name__ == "__main__":
      main()