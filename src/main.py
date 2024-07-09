import uvicorn
from fastapi import FastAPI
from src.models import Base
from src.database import engine

from .routers import products, aisles, departments, sections

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/healthy")
def health_check():
    return {"status": "Healthy"}


# app.include_router(auth.router)
app.include_router(products.router)
app.include_router(aisles.router)
app.include_router(departments.router)
app.include_router(sections.router)
# app.include_router(admin.router)
# app.include_router(users.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
