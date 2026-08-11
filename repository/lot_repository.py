from models.parking_lot import ParkingLot
from repository.db import get_connection
import logging

logger=logging.getLogger(__name__)

class LotRepository:
    def __init__(self):
        self.conn=get_connection()

    def save_lot(self,lot:ParkingLot):
        cursor=self.conn.cursor()
        cursor.execute('''
        INSERT INTO lots(lot_id,lot_name,car_rate,bike_rate,truck_rate)
        VALUES(?,?,?,?,?)
        ''',(lot.lot_id,lot.lot_name,lot.car_rate,lot.bike_rate,lot.truck_rate))
        self.conn.commit()

    def update_lot(self,lot:ParkingLot):
        self.conn.execute('''
        UPDATE lots SET car_rate=?, bike_rate=?, truck_rate=?
        WHERE lot_id=?
        ''',(lot.car_rate,lot.bike_rate,lot.truck_rate,lot.lot_id))
        self.conn.commit()

    def get_lot_by_id(self,lot_id):
        cursor=self.conn.cursor()
        cursor.execute('''
        SELECT * FROM lots WHERE lot_id=?
        ''',(lot_id,))
        row=cursor.fetchone()

        if row is None:
            return None
        return ParkingLot(
            lot_id=row["lot_id"],
            lot_name=row["lot_name"],
            car_rate=row["car_rate"],
            bike_rate=row["bike_rate"],
            truck_rate=row["truck_rate"]
        )
    def get_all_lots(self):
        cursor= self.conn.cursor()
        cursor.execute('''
        SELECT * FROM lots''')
        rows=cursor.fetchall()
        lots=[]
        for row in rows:
            lot=ParkingLot(
                lot_id=row["lot_id"],
                lot_name=row["lot_name"],
                car_rate=row["car_rate"],
                bike_rate=row["bike_rate"],
                truck_rate=row["truck_rate"]
            )
            lots.append(lot)
        return lots