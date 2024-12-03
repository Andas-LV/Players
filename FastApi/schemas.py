from datetime import datetime
from typing import Optional, ClassVar
from fastapi import UploadFile
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: str

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class UpdateAvatar(BaseModel):
    avatar_url: Optional[UploadFile]

class PlayerBase(BaseModel):
    id: int
    name: str
    full_name: str
    birth_date: datetime
    age: int
    height_cm: float
    weight_kgs: float
    positions: str
    nationality: str
    overall_rating: int
    potential: int
    value_euro: int | None
    wage_euro: int | None
    preferred_foot: str
    international_reputation: int = 5
    weak_foot: int = 5
    skill_moves: int = 5
    body_type: str
    release_clause_euro: Optional[float] = None
    national_team: Optional[str] = None
    national_rating: Optional[int] = None
    national_team_position: Optional[str] = None
    national_jersey_number: Optional[int] = None
    crossing: float
    finishing: float
    heading_accuracy: float
    short_passing: float
    volleys: float
    dribbling: float
    curve: float
    freekick_accuracy: float
    long_passing: float
    ball_control: float
    acceleration: float
    sprint_speed: float
    agility: float
    reactions: float
    balance: float
    shot_power: float
    jumping: float
    stamina: float
    strength: float
    long_shots: float
    aggression: float
    interceptions: float
    positioning: float
    vision: float
    penalties: float
    composure: float
    marking: float
    standing_tackle: float
    sliding_tackle: float

    class Config:
        from_attributes = True