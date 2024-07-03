# import os, sys

# root_path = os.path.dirname(__file__)
# sys.path.insert(0, root_path)

from fastapi import FastAPI
from models import Base
from database import engine

# from .routers import auth, todos, admin, users
from routers import items

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


# app.include_router(auth.router)
app.include_router(items.router)
# app.include_router(admin.router)
# app.include_router(users.router)
