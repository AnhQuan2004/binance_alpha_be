from pydantic import BaseModel, Field, HttpUrl, validator
from typing import Optional, List
from datetime import datetime, date, time as dt_time
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
    points: Optional[float] = Field(None, ge=0)
    amount: Optional[float] = Field(None, ge=0)
    event_date: date = Field(..., description="Event date (YYYY-MM-DD)")
    event_time: Optional[dt_time] = Field(None, description="Event time (HH:MM or HH:MM:SS)")
    timezone: Optional[str] = Field(None, description="e.g., Asia/Ho_Chi_Minh; defaults to UTC when omitted")
    phase: Optional[str] = Field(None, max_length=100)
    x: Optional[str] = None
    raised: Optional[str] = None
    source_link: Optional[str] = None
    image_url: Optional[str] = None

    @validator('event_time', pre=True)
    def empty_time_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @validator('timezone', pre=True)
    def empty_timezone_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @validator('timezone')
    def validate_timezone(cls, v):
        if v is not None:
            import pytz
            if v not in pytz.all_timezones:
                raise ValueError('Invalid timezone')
        return v

    @validator('points', 'amount', pre=True)
    def empty_numeric_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v


class AirdropCreate(AirdropBase):
    pass


class AirdropUpdate(BaseModel):
    project: Optional[str] = Field(None, min_length=1, max_length=100)
    alias: Optional[str] = Field(None, min_length=1, max_length=100)
    points: Optional[float] = Field(None, ge=0)
    amount: Optional[float] = Field(None, ge=0)
    event_date: Optional[date] = None
    event_time: Optional[dt_time] = None
    timezone: Optional[str] = None
    phase: Optional[str] = Field(None, max_length=100)
    x: Optional[str] = None
    raised: Optional[str] = None
    source_link: Optional[str] = None
    image_url: Optional[str] = None

    @validator('event_time', pre=True)
    def empty_time_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @validator('timezone', pre=True)
    def empty_timezone_to_none(cls, v):
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
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
    points: Optional[float]
    amount: Optional[float]
    event_date: Optional[str]
    event_time: Optional[str]
    timezone: Optional[str]
    phase: Optional[str]
    x: Optional[str]
    raised: Optional[str]
    source_link: Optional[str]
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    deleted: bool = False

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CoinData(BaseModel):
    coin_id: str
    time: datetime
    price: float


class CoinDataResponse(CoinData):
    id: str


class TokenBase(BaseModel):
    name: str
    apiUrl: str
    staggerDelay: int
    multiplier: float


class TokenCreate(TokenBase):
    pass


class TokenUpdate(BaseModel):
    name: Optional[str] = None
    apiUrl: Optional[str] = None
    staggerDelay: Optional[int] = None
    multiplier: Optional[float] = None


class TokenResponse(TokenBase):
    id: str


class AlphaInsightBase(BaseModel):
    title: str
    category: str
    token: str
    platform: str
    raised: str
    description: str
    date: str
    imageUrl: Optional[str] = None
    url: Optional[str] = None


class AlphaInsightCreate(AlphaInsightBase):
    pass


class AlphaInsightUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    token: Optional[str] = None
    platform: Optional[str] = None
    raised: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    imageUrl: Optional[str] = None
    url: Optional[str] = None


class AlphaInsightResponse(AlphaInsightBase):
    id: str


class AccountBase(BaseModel):
    name: str
    balance: float
    alphaPoints: float


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[float] = None
    alphaPoints: Optional[float] = None


class AccountResponse(AccountBase):
    id: str


class AirdropItem(BaseModel):
    token: str
    amount: float
    price: float
    value: float


class TransactionBase(BaseModel):
    accountId: str
    date: str
    alphaPoints: float
    initialBalance: float
    finalBalance: float
    tradeFee: float
    note: Optional[str] = None
    airdrops: List[AirdropItem] = []
    # Legacy fields
    airdropToken: Optional[str] = None
    airdropAmount: Optional[float] = None
    airdropTokenPrice: Optional[float] = None
    pnl: float
    alphaReward: float
    airdropValue: Optional[float] = None
    totalClaim: float


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    accountId: Optional[str] = None
    date: Optional[str] = None
    alphaPoints: Optional[float] = None
    initialBalance: Optional[float] = None
    finalBalance: Optional[float] = None
    tradeFee: Optional[float] = None
    note: Optional[str] = None
    airdrops: Optional[List[AirdropItem]] = None
    airdropToken: Optional[str] = None
    airdropAmount: Optional[float] = None
    airdropTokenPrice: Optional[float] = None
    pnl: Optional[float] = None
    alphaReward: Optional[float] = None
    airdropValue: Optional[float] = None
    totalClaim: Optional[float] = None


class TransactionResponse(TransactionBase):
    id: str
