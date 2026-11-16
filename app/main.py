from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes.restaurants import router as restaurant_router
from app.services.exceptions import (BusinessRuleError, DomainError, ForbiddenError, NotFoundError,)

from app.routes.menus import router as menu_router

app = FastAPI(title="SnackOverflow API")

# Error family -> HTTP status.
STATUS_CODES = {NotFoundError: 404, BusinessRuleError: 409, ForbiddenError: 403}


@app.get("/health")
def health():
    return {"status": "ok"}


# Catches every DomainError subclass.
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    # First matching family's status, else 500.
    status_code = next(
        (code for cls, code in STATUS_CODES.items() if isinstance(exc, cls)),
        500,
    )
    # Same {"detail": ...} shape as FastAPI errors.
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})

app.include_router(restaurant_router)
app.include_router(menu_router)

frontend_dir = Path(__file__).resolve().parent / "frontend"


@app.get("/management", include_in_schema=False)
def management_frontend():
    return FileResponse(frontend_dir / "management.html")


app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
