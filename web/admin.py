from fastapi import FastAPI

from src.database import init_db
from web.routes import (
    analytics_router,
    categories_router,
    dashboard_router,
    orders_router,
    payments_router,
    pricing_router,
    products_router,
    settings_router,
    support_router,
    system_router,
    topups_router,
    users_router,
)

app = FastAPI(title="NanoToolz Admin Panel", version="2.0.0")


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


app.include_router(dashboard_router)
app.include_router(products_router)
app.include_router(pricing_router)
app.include_router(categories_router)
app.include_router(users_router)
app.include_router(orders_router)
app.include_router(payments_router)
app.include_router(topups_router)
app.include_router(settings_router)
app.include_router(support_router)
app.include_router(analytics_router)
app.include_router(system_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
