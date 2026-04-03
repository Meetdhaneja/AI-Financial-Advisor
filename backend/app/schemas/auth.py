from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    monthly_income_default: float | None = None
    risk_profile: str = "medium"
    monthly_budget_target: float | None = None
    preferred_savings_rate: float | None = None
    category_budget_preferences: dict[str, float] | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(ORMModel):
    id: int
    email: EmailStr
    full_name: str
    monthly_income_default: float | None = None
    risk_profile: str
    monthly_budget_target: float | None = None
    preferred_savings_rate: float | None = None
    category_budget_preferences: dict[str, float] | None = None
    created_at: datetime


class UserPreferencesUpdate(BaseModel):
    monthly_income_default: float | None = None
    monthly_budget_target: float | None = None
    preferred_savings_rate: float | None = None
    risk_profile: str | None = None
    category_budget_preferences: dict[str, float] | None = None
