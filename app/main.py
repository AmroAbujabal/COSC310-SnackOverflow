from fastapi import FastAPI

from app.routes.restaurants import router as restaurant_router

from app.routes.menus import router as menu_router

app = FastAPI(title="SnackOverflow API")


@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(restaurant_router)
app.include_router(menu_router)