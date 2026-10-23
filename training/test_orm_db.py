from sqlalchemy import text
from database_orm import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT VERSION()"))
        print("Connected to MySQL!")
        print("MySQL version:", result.scalar())
finally:
    engine.dispose()