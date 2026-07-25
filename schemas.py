from pydantic import BaseModel, Field
from datetime import datetime

class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    date: datetime

    class Config:
        from_attributes= True

class Matchget(MatchCreate):
    id: int

class RefereeCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str = Field(..., pattern=r"^\d{9}")

    class Config:
        from_attributes = True

class RefereeGet(RefereeCreate):
    id: int

class MatchAssignmentCreate(BaseModel):
    match_id: int
    ref_id: int
    role: str

class MatchAssignmentGet(MatchAssignmentCreate):
    id: int
    
    match: Matchget
    referee: RefereeGet

    class Config:
        from_attributes = True


class RefereeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = Field(None, pattern=r"^\d{9}")


        
