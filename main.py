import uvicorn
from fastapi import FastAPI
from models import Base
from database import engine

# from .routers import auth, todos, admin, users
from routers import products, aisles, departments

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


# app.include_router(auth.router)
app.include_router(products.router)
app.include_router(aisles.router)
app.include_router(departments.router)
# app.include_router(admin.router)
# app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
