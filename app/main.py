from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routes.restaurants import router as restaurant_router
from app.services.exceptions import RestaurantNotFoundError

app = FastAPI(title="SnackOverflow API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(RestaurantNotFoundError)
async def restaurant_not_found(request: Request, exc: RestaurantNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

app.include_router(restaurant_router)
