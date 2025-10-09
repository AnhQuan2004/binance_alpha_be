from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}


class AirdropBase(BaseModel):
    project: str = Field(..., min_length=1, max_length=100)
    alias: str = Field(..., min_length=1, max_length=100)
    points: float = Field(..., ge=0)
    amount: float = Field(..., ge=0)
    time_iso: str = Field(..., description="ISO format: 2025-10-08T14:00:00+07:00")
    timezone: str = Field(..., description="e.g., Asia/Ho_Chi_Minh")
    phase: Optional[str] = Field(None, max_length=100)
    x: Optional[str] = None
    raised: Optional[float] = Field(None, ge=0)
    source_link: Optional[str] = None

    @validator('time_iso')
    def validate_time_iso(cls, v):
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid ISO datetime format')
        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        import pytz
        if v not in pytz.all_timezones:
            raise ValueError('Invalid timezone')
        return v


class AirdropCreate(AirdropBase):
    pass


class AirdropUpdate(BaseModel):
    project: Optional[str] = Field(None, min_length=1, max_length=100)
    alias: Optional[str] = Field(None, min_length=1, max_length=100)
    points: Optional[float] = Field(None, ge=0)
    amount: Optional[float] = Field(None, ge=0)
    time_iso: Optional[str] = None
    timezone: Optional[str] = None
    phase: Optional[str] = Field(None, max_length=100)
    x: Optional[str] = None
    raised: Optional[float] = Field(None, ge=0)
    source_link: Optional[str] = None

    @validator('time_iso')
    def validate_time_iso(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid ISO datetime format')
        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None:
            import pytz
            if v not in pytz.all_timezones:
                raise ValueError('Invalid timezone')
        return v


class AirdropInDB(AirdropBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime
    deleted: bool = False

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AirdropResponse(BaseModel):
    id: str
    project: str
    alias: str
    points: float
    amount: float
    time_iso: str
    timezone: str
    phase: Optional[str]
    x: Optional[str]
    raised: Optional[float]
    source_link: Optional[str]
    created_at: datetime
    updated_at: datetime
    deleted: bool = False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
