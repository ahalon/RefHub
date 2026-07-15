from fastapi import FastAPI, Depends, HTTPException, status
from database.database import engine, SessionLocal, Base
from database.models import RefereeDB
from sqlalchemy.orm import Session
from typing import List
import schemas

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.post("/referees")
def create_referee(referee: schemas.RefereeCreate, db: Session = Depends(get_db)):
    db_referee = Referee(
        first_name = referee.first_name,
        last_name = referee.last_name,
        phone_number = referee.phone_number)
    db.add(db_referee)
    db.commit()
    db.refresh(db_referee)
    return db_referee

@app.get("/referees", response_model=List[schemas.RefereeGet])
def retrieve_referees(db: Session = Depends(get_db)):
    refs = db.query(RefereeDB).all()
    return refs

@app.get("/referees/{ref_id}", response_model=schemas.RefereeGet)
def retreive_referees_by_id(ref_id: int, db: Session = Depends(get_db)):
    ref= db.query(RefereeDB).filter(RefereeDB.id == ref_id).first()
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Referee doesn't exist"
        )
    return ref

    



@app.get("/")
def Hello():
    return {"message" : "Hello"}