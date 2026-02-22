import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class BroadcastSegment(str, enum.Enum):
    all = "all"
    subscribers = "subscribers"
    tag = "tag"


class BroadcastStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    completed = "completed"
    failed = "failed"


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {"text": "...", "photo": "...", "video": "..."}
    segment: Mapped[BroadcastSegment] = mapped_column(Enum(BroadcastSegment), nullable=False)
    segment_tag: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[BroadcastStatus] = mapped_column(Enum(BroadcastStatus), default=BroadcastStatus.draft, nullable=False)
    stats: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # {"total": N, "sent": N, "failed": N}
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<Broadcast id={self.id} segment={self.segment} status={self.status}>"
