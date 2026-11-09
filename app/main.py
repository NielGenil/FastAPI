from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, products, orders, categories

Base.metadata.create_all(bind=engine)   # creates tables if missing (fine for learning)

app = FastAPI(title="Store API")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(categories.router)