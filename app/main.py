from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.routes import account_route
from app.services.account_service import (
    AccountError, Unauthenticated, Forbidden, AccountConflict, AccountNotFound,
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import restaurant_route, menu_item_route, order_route, shopping_cart_route

# uvicorn app.main:app --reload
# http://127.0.0.1:8000/docs

async def account_error(request: Request, error: AccountError) -> JSONResponse:
    codes = {Unauthenticated: 401, Forbidden: 403, AccountConflict: 409, AccountNotFound: 404}
    return JSONResponse(status_code=codes.get(type(error), 400),
                        content={"detail": str(error)})


async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    # Pydantic's default error payload includes input values, including passwords.
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
               for e in error.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


def root():
    return {"message": "Backend is running"}


def health():
    return {"status": "ok"}


def is_local_demo_request(request: Request) -> bool:
    loopback_hosts = {"127.0.0.1", "::1"}
    return (
        request.client is not None
        and request.client.host in loopback_hosts
        and request.url.hostname in loopback_hosts | {"localhost"}
    )


def require_local_demo_request(request: Request) -> None:
    if not is_local_demo_request(request):
        raise Forbidden("Demo menu editing is only available on localhost.")


def create_app(*, local_menu_edits: bool = False) -> FastAPI:
    application = FastAPI(title="COSC 310 Team 19 Food Delivery", version="M2")
    application.add_exception_handler(AccountError, account_error)
    application.add_exception_handler(RequestValidationError, validation_error)
    for router in (restaurant_route.router, account_route.router, menu_item_route.router,
                   order_route.router, shopping_cart_route.router):
        application.include_router(router)

    if local_menu_edits:
        application.dependency_overrides[menu_item_route.require_menu_editor] = require_local_demo_request

    @application.get("/ui-config", include_in_schema=False)
    def ui_config(request: Request) -> dict[str, bool]:
        return {"local_menu_edits": local_menu_edits and is_local_demo_request(request)}

    application.add_api_route("/", root)
    application.add_api_route("/health", health)
    application.mount(
        "/ui",
        StaticFiles(directory=Path(__file__).resolve().parent / "frontend", html=True),
        name="frontend",
    )
    return application


def create_local_demo_app() -> FastAPI:
    return create_app(local_menu_edits=True)


app = create_app()
