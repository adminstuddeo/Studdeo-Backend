from datetime import datetime
from uuid import UUID

from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class PasswordResetToken(Base):
    __tablename__: str = "password_reset_token"

    token: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    id_user: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=False)
    expired_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )

    user: Mapped[User] = relationship()
