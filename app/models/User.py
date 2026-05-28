from sqlalchemy import Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional, List

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(250), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(250), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    photo: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def __str__(self) -> str:
        return f"User(id={self.id}, title='{self.name}')"
