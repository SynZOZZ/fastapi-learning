from fastapi import FastAPI
from app.database import engine, Base
import app.models
from app.routers import users

Base.metadata.create_all(bind=engine)  # creates tables automatically

app = FastAPI(title="FastAPI-Learning")
app.include_router(users.router)


@app.get("/")
def root():
    return {"message": "FastAPI is running!"}
