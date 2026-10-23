from enum import Enum

from pydantic import BaseModel, Field

class ShipmentStatus(str, Enum):
    placed = "placed"
    in_transit = "in_transit"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"

class BaseShipment(BaseModel):
      content: str = Field(max_length = 100)
      weight: float = Field(description="weight in kgm",le=500, ge=1)
      destination: str = Field(default = None)


class ShipmentRead(BaseShipment):
      status: ShipmentStatus

class ShipmentCreate(BaseShipment):
      pass

class ShipmentUpdate(BaseModel):
    status: ShipmentStatus
