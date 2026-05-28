from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import Optional

from app.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    users: Mapped["User"] = relationship("User", back_populates="role")

    def __str__(self) -> str:
        return f"Role(id={self.id}, title='{self.name}')"
