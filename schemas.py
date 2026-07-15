from pydantic import BaseModel

class RefereeCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str

    class Config:
        from_attributes = True

class RefereeGet(RefereeCreate):
    id: int

