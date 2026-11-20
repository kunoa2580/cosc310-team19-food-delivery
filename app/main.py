from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.routes import account_route
from app.services.account_service import (
    AccountError, Unauthenticated, Forbidden, AccountConflict, AccountNotFound,
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import restaurant_route, menu_item_route, order_route

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

app = FastAPI(
    title="COSC 310 Team 19 Food Delivery",
    version="M1",
)

app.include_router(restaurant_route.router)
app.include_router(account_route.router)


@app.exception_handler(AccountError)
async def account_error(request: Request, error: AccountError) -> JSONResponse:
    codes = {Unauthenticated: 401, Forbidden: 403, AccountConflict: 409, AccountNotFound: 404}
    return JSONResponse(status_code=codes.get(type(error), 400),
                        content={"detail": str(error)})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    # Pydantic's default error payload includes input values, including passwords.
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
               for e in error.errors()]
    return JSONResponse(status_code=422, content={"detail": details})
# feature/menu-item-schema
# To add router for menu item for users could view, create, edit and remove item details like price, name or etc. 
app.include_router(menu_item_route.router)
app.include_router(order_route.router)

# Serve the plain HTML/CSS/JavaScript frontend from the same origin as the API.
app.mount(
    "/ui",
    StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True),
    name="frontend",
)

@app.get("/")
def root():
    return {"message": "Backend is running"}


@app.get("/health", status_code=200)
def health():
    return {"status": "ok"}
