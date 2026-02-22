import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    user = "user"
    manager = "manager"
    admin = "admin"


class UserStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="user")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id}>"
