import sqlite3

connection = sqlite3.connect("sqlite.db")
cursor = connection.cursor()


# create a table
cursor.execute(
    """CREATE TABLE IF NOT EXISTS shipment (
        id INTEGER PRIMARY KEY,
        content TEXT,
        weight REAL,
        status TEXT,
        destination TEXT
    )"""
)
connection.commit()

# update a shipment
# cursor.execute(
#     """
#     UPDATE shipment SET status = "in_transit
#     """
# )

# cursor.execute("DROP TABLE shipment")
# connection.commit()

# id=12
# status="in_transit"

# cursor.execute(
#     f"""
#     UPDATE shipment SET status = '{status}'
#     where id = {id}
#     """
# )
# connection.commit()

# id = 13
# status = "in_transit"

# cursor.execute(
#     """
#     UPDATE shipment SET status = ?
#     where id = ?
#     """
# ,(status, id))
# connection.commit()

# cursor.execute(
#     """
#     UPDATE shipment SET status = :status
#     where id = :id
#     """
# ,{"status": status, "id": id})
# connection.commit()

# add shipment data
# cursor.execute(
#     """
#     INSERT INTO shipment
#     VALUES (13, "dog food",0.5,"placed","vizag")
#     """
# )
# connection.commit()

# read a shipment by id
# cursor.execute(
#     """
#      SELECT * FROM shipment 
#     """
# )
# result = cursor.fetchall()
# print(result)

# delete a shipment by id
# cursor.execute(
#     """
#     DELETE FROM shipment
#     where id =12
#     """
# )
# conection.commit()


# `main.py` currently uses this dictionary and calls save() after changes.
shipments = {}


def save():
    cursor.executemany(
        """INSERT OR REPLACE INTO shipment
           (id, content, weight, status, destination)
           VALUES (?, ?, ?, ?, ?)""",
        [
            (id, item["content"], item["weight"], item["status"], item.get("destination"))
            for id, item in shipments.items()
        ],
    )
    connection.commit()
