from datetime import UTC, datetime
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class Link(Base):
    __tablename__ = "links"
    id: Mapped[int] = mapped_column(primary_key=True)
    original_url: Mapped[str]
    short_code: Mapped[str | None] = mapped_column(unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    expires_at: Mapped[datetime | None] = mapped_column(
    nullable=True,
    default=None,
)