from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.database import SessionLocal
from database.models import MatchAssignmentDB, MatchDB
import schemas

router = APIRouter(
    prefix="/assignments",
    tags=["assignments"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", response_model=schemas.MatchAssignmentGet, status_code=status.HTTP_201_CREATED)
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

@router.get("", response_model=List[schemas.MatchAssignmentGet])
def retrieve_assignments(ref_id: int | None = None, db: Session = Depends(get_db)):
    assign = db.query(MatchAssignmentDB)

    if ref_id is not None:
        assign = assign.filter(MatchAssignmentDB.ref_id == ref_id)

    return assign.all()