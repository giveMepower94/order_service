import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.order_service.infrastructure.db.base import Base
from src.order_service.domain.enums import OrderStatus


class OrderModel(Base):
    __tablename__ = "orders"

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_orders_idempotency_key"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    item_id: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        String(50), nullable=False, default=OrderStatus.NEW
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
