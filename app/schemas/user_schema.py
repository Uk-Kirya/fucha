from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, computed_field
import pytz

moscow_tz = pytz.timezone("Europe/Moscow")


class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    photo: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field(return_type=Optional[str])
    @property
    def last_login_msk(self) -> Optional[str]:
        if self.last_login:
            return self.last_login.astimezone(moscow_tz).strftime("%Y-%m-%d в %H:%M")
        return f"—"

    @computed_field(return_type=Optional[str])
    @property
    def created_at_msk(self) -> Optional[str]:
        return self.created_at.astimezone(moscow_tz).strftime("%Y-%m-%d в %H:%M")

    @computed_field(return_type=Optional[str])
    @property
    def updated_at_msk(self) -> Optional[str]:
        return self.updated_at.astimezone(moscow_tz).strftime("%Y-%m-%d в %H:%M")


class RoleBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str

    model_config = {"extra": "forbid"}


class UserWithRole(UserBase):
    role: RoleBase
