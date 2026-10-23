from sqlalchemy import String, DateTime, func, ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .orm_models import Base



class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(
        primary_key = True,
        autoincrement = True
    )

    content: Mapped[str] = mapped_column(
        String(500),
        nullable = False,
    )

    destination: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.now(),
    )

    customer_id: Mapped[int | None] = mapped_column(
        ForeignKey("customers.id"),
        nullable= True,
    )

    customer: Mapped["Customer | None"] = relationship(
        "Customer", back_populates="shipments"
    )
