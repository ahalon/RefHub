from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import MatchDB
import schemas

router = APIRouter(
    prefix="/matches",
    tags=["matches"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", status_code=status.HTTP_201_CREATED)
def add_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    db_match = MatchDB(
        homet_team = match.home_team,
        away_team=match.away_team,
        date=match.date
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match