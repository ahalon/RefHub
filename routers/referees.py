from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.database import SessionLocal
from database.models import RefereeDB
import schemas

router = APIRouter(
    prefix="/referees",
    tags=["referees"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=schemas.RefereeGet, status_code=status.HTTP_201_CREATED)
def create_referee(referee: schemas.RefereeCreate, db: Session = Depends(get_db)):
    db_referee= RefereeDB(
        first_name = referee.first_name,
        last_name = referee.last_name,
        phone_number = referee.phone_number
    )

    db.add(db_referee)
    db.commit()
    db.refresh(db_referee)
    return db_referee

@router.get("", response_model=List[schemas.RefereeGet])
def retrieve_referees(db: Session = Depends(get_db)):
    return db.query(RefereeDB).all()

router.get("/{ref_id}", response_model=schemas.RefereeGet)
def retrieve_referee_by_id(ref_id: int, db: Session = Depends(get_db)):
    ref= db.query(RefereeDB).filter(RefereeDB.id==ref.id).first()
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referee doesn't exist"
        )
    return ref

router.patch("/{ref_id}", response_model=schemas.RefereeGet)
def update_referee(ref_id: int, referee_update: schemas.RefereeUpdate, db: Session = Depends(get_db)):
    db_referee = db.query(RefereeDB).filter(RefereeDB.id == ref_id).first()
    if db_referee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referee doesn't exist"
        )

    update_data = referee_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_referee, key, value)

    db.commit()
    db.refresh(db_referee)
    return db_referee

@router.delete("{ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_referee(ref_id: int, db: Session = Depends(get_db)):
    ref = db.query(RefereeDB).filter(RefereeDB.id == ref_id).first()
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referee doesnt't exist")
    db.delete(ref)
    db.commit()
    return None