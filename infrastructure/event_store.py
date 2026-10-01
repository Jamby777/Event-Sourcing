import sqlite3
import pickle
from typing import List
from domain.events import Event

DB_FILE = "bank_events.db"

class EventStore:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    event_data BLOB NOT NULL
                )
            """)
            conn.commit()

    def append(self, account_id: str, events: List[Event]) -> None:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            for event in events:
                # Serializamos el objeto del evento con pickle para guardarlo completo
                serialized = pickle.dumps(event)
                cursor.execute(
                    "INSERT INTO events (account_id, event_data) VALUES (?, ?)",
                    (account_id, serialized)
                )
            conn.commit()

    def get_events_for(self, account_id: str) -> List[Event]:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT event_data FROM events WHERE account_id = ? ORDER BY id ASC",
                (account_id,)
            )
            rows = cursor.fetchall()
            return [pickle.loads(row[0]) for row in rows]