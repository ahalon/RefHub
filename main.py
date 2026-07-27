from fastapi import FastAPI, Depends, HTTPException, status
from database.database import engine, SessionLocal, Base
from database.models import RefereeDB, MatchDB, MatchAssignmentDB
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

# --- REFEREES ---

@app.post("/referees", response_model=schemas.RefereeGet, status_code=status.HTTP_201_CREATED)
def create_referee(referee: schemas.RefereeCreate, db: Session = Depends(get_db)):
    db_referee = RefereeDB(
        first_name=referee.first_name,
        last_name=referee.last_name,
        phone_number=referee.phone_number
    )
    db.add(db_referee)
    db.commit()
    db.refresh(db_referee)
    return db_referee

@app.get("/referees", response_model=List[schemas.RefereeGet])
def retrieve_referees(db: Session = Depends(get_db)):
    return db.query(RefereeDB).all()

@app.get("/referees/{ref_id}", response_model=schemas.RefereeGet)
def retrieve_referee_by_id(ref_id: int, db: Session = Depends(get_db)):
    ref = db.query(RefereeDB).filter(RefereeDB.id == ref_id).first()
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referee doesn't exist"
        )
    return ref

@app.patch("/referees/{ref_id}", response_model=schemas.RefereeGet)
def update_referee(
    ref_id: int,
    referee_update: schemas.RefereeUpdate,
    db: Session = Depends(get_db)
):
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

@app.delete("/referees/{ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_referee(ref_id: int, db: Session = Depends(get_db)):
    ref = db.query(RefereeDB).filter(RefereeDB.id == ref_id).first()
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Referee doesn't exist"
        )

    db.delete(ref)
    db.commit()
    return None

# --- MATCHES ---

@app.post("/matches", status_code=status.HTTP_201_CREATED)
def add_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    db_match = MatchDB(
        home_team=match.home_team,
        away_team=match.away_team,
        date=match.date
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

# --- ASSIGNMENTS ---

@app.post("/assignments", response_model=schemas.MatchAssignmentGet, status_code=status.HTTP_201_CREATED)
def create_assignment(assignment: schemas.MatchAssignmentCreate, db: Session = Depends(get_db)):
    existing_assignment = db.query(MatchAssignmentDB).filter(
        MatchAssignmentDB.match_id == assignment.match_id,
        MatchAssignmentDB.ref_id == assignment.ref_id
    ).first()

    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This referee is already assigned to this match"
        )

    target_match = db.query(MatchDB).filter(MatchDB.id == assignment.match_id).first()
    if not target_match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    time_conflict = db.query(MatchAssignmentDB).join(MatchDB).filter(
        MatchAssignmentDB.ref_id == assignment.ref_id,
        MatchDB.date == target_match.date
    ).first()

    if time_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This referee already has another match at the exact same time"
        )

    db_assignment = MatchAssignmentDB(
        match_id=assignment.match_id,
        ref_id=assignment.ref_id,
        role=assignment.role
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

@app.get("/assignments", response_model=List[schemas.MatchAssignmentGet])
def retrieve_assignments(ref_id: int | None = None, db: Session = Depends(get_db)):
    assign = db.query(MatchAssignmentDB)

    if ref_id is not None:
        assign = assign.filter(MatchAssignmentDB.ref_id == ref_id)

    return assign.all()