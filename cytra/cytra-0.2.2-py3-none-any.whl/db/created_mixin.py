from datetime import datetime

from sqlalchemy import DateTime, Column


class CreatedMixin:
    created_at = Column(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
    )
