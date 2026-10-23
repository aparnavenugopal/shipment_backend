from typing import Any

class City:
    def __init__(self, name, location):
        self.name = name
        self.location = location

hamshire = City("hyd", 204857)

text: str = "value"
pert: int = 90
temp: float = 37.5

number: int | float = 12

digits: list[int] = [1,2,3,4,5]

table_5: tuple[int, ...] = (5,3,1,3)

city_temp: tuple[str, float] = ("city", 20.5)

def root(num: int | float, exp: float | None = .5) -> float:
    return pow(num, .5)

root_25 = root(25)

shipment: dict[str, str | int | float] = {
    "id": 1293,
    "weight": 1.2,
    "content": "wooden table",
    "status": "in transit"
}