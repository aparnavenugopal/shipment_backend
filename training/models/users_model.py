from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from .orm_models import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key = True,
        autoincrement = True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False,
        index = True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    customer: Mapped["Customer | None"] = relationship(
        back_populates = "user",
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable = False,
        default = "customer",
    )
