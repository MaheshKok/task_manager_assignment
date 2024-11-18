import datetime
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import String

from task_manager.db.base import Base


class TaskDBModel(Base):
    """Model for Task."""

    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(length=200))
    description: Mapped[str] = mapped_column(String(length=500))
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.utcnow,
    )

    # Add the foreign key
    user_id: Mapped[uuid] = mapped_column(ForeignKey("user.id"))
    # Add a relationship to the user model (optional, but useful)
    user: Mapped["user"] = relationship("UserDBModel", back_populates="tasks")
