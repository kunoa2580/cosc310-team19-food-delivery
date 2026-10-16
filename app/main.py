from fastapi import FastAPI, HTTPException
from app.api.routes import restaurant_route, menu_item_route

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

app = FastAPI(title="We will go through this semester like every other semester", version="0.0.0.0.1")

app.include_router(restaurant_route.router)
# feature/menu-item-schema
# To add router for menu item for users could view, create, edit and remove item details like price, name or etc. 
app.include_router(menu_item_route.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}