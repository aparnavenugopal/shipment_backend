import sqlite3
from typing import Any

from learn.schemas import ShipmentCreate, ShipmentUpdate


class Database:

    def __init__(self):
        # Create connection to SQLite database
        self.conn = sqlite3.connect(
            "sqlite.db",
            check_same_thread= False
        )

        # Cursor is used to execute SQL queries
        self.cur = self.conn.cursor()

        # Create table when Database object is initialized
        self.create_table()

    def create_table(self):
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS shipment (
                id INTEGER PRIMARY KEY,
                content TEXT,
                weight REAL,
                status TEXT
            )
            """
        )

        self.conn.commit()

    # -----------------------------
    # CREATE
    # -----------------------------
    def create(self, shipment: ShipmentCreate) -> dict[str, int]:

        # Find the current maximum ID
        self.cur.execute(
            "SELECT MAX(id) FROM shipment"
        )

        result = self.cur.fetchone()

        # If table is empty, start from 1
        new_id = (result[0] or 0) + 1

        # Insert shipment into database
        self.cur.execute(
            """
            INSERT INTO shipment
            VALUES (:id, :content, :weight, :status)
            """,
            {
                "id": new_id,
                **shipment.model_dump(),
                "status": "placed",
            }
        )

        self.conn.commit()

        return {
            "id": new_id
        }

    # -----------------------------
    # GET BY ID
    # -----------------------------
    def get(self, id: int) -> dict[str, Any] | None:

        self.cur.execute(
            """
            SELECT *
            FROM shipment
            WHERE id = ?
            """,
            (id,)
        )

        row = self.cur.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "status": row[3],
        }

    # -----------------------------
    # GET LATEST
    # -----------------------------
    def get_latest(self) -> dict[str, Any] | None:

        self.cur.execute(
            """
            SELECT *
            FROM shipment
            ORDER BY id DESC
            LIMIT 1
            """
        )

        row = self.cur.fetchone()

        if row is None:
            return None

        return {
            "id": row[0],
            "content": row[1],
            "weight": row[2],
            "status": row[3],
        }

    # -----------------------------
    # UPDATE
    # -----------------------------
    def update(
        self,
        id: int,
        shipment: ShipmentUpdate
    ) -> dict[str, Any] | None:

        # Check whether shipment exists
        existing = self.get(id)

        if existing is None:
            return None

        # Only update fields supplied by the client
        data = shipment.model_dump(exclude_unset=True)

        if data:
            set_clause = ", ".join(
                f"{field} = :{field}"
                for field in data
            )

            data["id"] = id

            self.cur.execute(
                f"""
                UPDATE shipment
                SET {set_clause}
                WHERE id = :id
                """,
                data
            )

            self.conn.commit()

        return self.get(id)

    # -----------------------------
    # DELETE
    # -----------------------------
    def delete(self, id: int) -> bool:

        self.cur.execute(
            """
            DELETE FROM shipment
            WHERE id = ?
            """,
            (id,)
        )

        self.conn.commit()

        # rowcount tells us whether a row was actually deleted
        return self.cur.rowcount > 0

    # -----------------------------
    # CLOSE CONNECTION
    # -----------------------------
    def close(self):
        self.conn.close()


