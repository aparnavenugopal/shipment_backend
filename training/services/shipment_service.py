from ..database import get_connection

def get_all_shipments():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id, content, destination, status, customer_id
            FROM shipments
            """
        )

        return cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

def insert_shipment(
    content: str,
    destination: str,
    status: str,
    customer_id: int | None = None,
):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            INSERT INTO shipments (content, destination, status, customer_id)
            values (%s, %s, %s, %s)
            """,
            (content, destination, status, customer_id),
        )
        connection.commit()
        shipment_id = cursor.lastrowid
        customer = None
        if customer_id is not None:
            cursor.execute(
                "SELECT id, name FROM customers WHERE id = %s",
                (customer_id,),
            )
            customer = cursor.fetchone()

        return {
            "id": shipment_id,
            "content": content,
            "destination": destination,
            "status": status,
            "customer_id": customer_id,
            "customer": customer,
        }

    finally:
        cursor.close()
        connection.close()

def get_shipment_by_id(shipment_id: int):
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT * FROM shipments WHERE id = %s
            """,
            (shipment_id, )
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

def update_shipment_part(shipment_id: int, updates: dict):
    if not updates:
        return get_shipment_by_id(shipment_id)

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        fields = ", ".join(f"{field} = %s" for field in updates)

        cursor.execute(
            f"UPDATE shipments SET {fields} WHERE id = %s",
            (*updates.values(), shipment_id),
        )
        connection.commit()

        return get_shipment_by_id(shipment_id)
    finally:
        cursor.close()
        connection.close()

def update_shipment(shipment_id: int,updates: dict):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        fields = ", ".join(f"{field} = %s" for field in updates)
        cursor.execute(
           f"UPDATE shipments SET {fields} where id = %s",
           (*updates.values(), shipment_id)
        )
        connection.commit()
    finally:
        cursor.close()
        connection.close()

    return get_shipment_by_id(shipment_id)

def delete_shipment(shipment_id: int) -> bool:
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            f"DELETE FROM shipments WHERE id = %s",
            (shipment_id, )
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return False

        connection.commit()
        return True
    finally:
        cursor.close()
        connection.close()
