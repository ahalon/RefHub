from database.database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey

class RefereeDB(Base):
    __tablename__ = "referee"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone_number = Column(String, unique= True)

class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True)
    home_team = Column(String)
    away_team = Column(String)
    date = Column(DateTime)


class MatchAssignment(Base):
    __tablename__ = "match_assignment"
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("match.id"))
    ref_id = Column(Integer, ForeignKey("referee.id"))
    role = Column(String)