from database import get_connection

connection = get_connection()

try:
    cursor = connection.cursor()
    cursor.execute("SELECT VERSION()")

    result = cursor.fetchone()
    print("Connected to MySQL!")
    print("MySQL version:", result[0])

    cursor.close()
finally:
    connection.close()


