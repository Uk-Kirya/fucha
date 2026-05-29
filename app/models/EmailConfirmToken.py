import secrets
from datetime import datetime, timedelta
from sqlalchemy import Integer, ForeignKey, DateTime, Boolean, String
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


class EmailConfirmToken(Base):
    __tablename__ = "email_confirm_token"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, index=True, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime, unique=True, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    @staticmethod
    def generate(user_id: int, expires_minutes: int = 30):
        return EmailConfirmToken(
            user_id=user_id,
            token=str(secrets.token_urlsafe(32)),
            expires_at=datetime.now() + timedelta(minutes=expires_minutes),
        )
