from fastapi import FastAPI
from database.database import engine, Base
from routers import referees, matches, assignments

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(referees.router)
app.include_router(matches.router)
app.include_router(assignments.router)