from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .shipment_models import Shipment
from .users_model import User
from .orm_models import Base

class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    shipments: Mapped[list["Shipment"]] = relationship(
        "Shipment", back_populates="customer"
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique = True,
        nullable=True,
    )

    user: Mapped["User | None"] = relationship(
        back_populates = "customer",
    )

