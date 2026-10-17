from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes.restaurants import router as restaurant_router
from app.services.exceptions import (RestaurantNotFoundError, MenuItemNotFoundError,)

from app.routes.menus import router as menu_router

app = FastAPI(title="SnackOverflow API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(RestaurantNotFoundError)
async def restaurant_not_found(request: Request, exc: RestaurantNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(MenuItemNotFoundError)
async def menu_item_not_found_handler(
    request: Request,
    exc: MenuItemNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )

app.include_router(restaurant_router)
app.include_router(menu_router)

frontend_dir = Path(__file__).resolve().parent / "frontend"


@app.get("/management", include_in_schema=False)
def management_frontend():
    return FileResponse(frontend_dir / "management.html")


app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
