from sqlalchemy.orm import DeclarativeBase

from task_manager.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
