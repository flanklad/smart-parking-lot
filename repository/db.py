import sqlite3
import logging

logger = logging.getLogger(__name__)

_connection = None

def get_connection(db_path="parking.db") -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(db_path)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON")
        _create_tables(_connection)
        logger.debug(f"Connected to {db_path}")
    return _connection


def _create_tables(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS lots(
          lot_id TEXT PRIMARY KEY,
          lot_name TEXT NOT NULL,
          car_rate REAL NOT NULL,
          bike_rate REAL NOT NULL,
          truck_rate REAL NOT NULL
          )
        ''')
    conn.execute('''
          CREATE TABLE IF NOT EXISTS slots(
              slot_id     TEXT PRIMARY KEY,
              slot_type   TEXT NOT NULL,
              slot_status TEXT NOT NULL,
              vehicle_no  TEXT,
              lot_id TEXT NOT NULL REFERENCES lots(lot_id)
          )''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS tickets(
      ticket_id    TEXT PRIMARY KEY,
      slot_id      TEXT NOT NULL REFERENCES slots(slot_id),
      vehicle_no   TEXT NOT NULL,
      vehicle_type TEXT NOT NULL,
      entry_time   DATETIME NOT NULL,
      exit_time    DATETIME,
      fees         REAL,
      lot_id       TEXT NOT NULL REFERENCES lots(lot_id)
      )''')

    conn.commit()
    logger.debug(f"Tables created")

