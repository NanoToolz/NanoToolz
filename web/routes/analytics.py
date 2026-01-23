from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Order, Product, User
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_products = db.query(Product).count()
    total_revenue = sum(float(o.price_paid_usd or 0) for o in db.query(Order).all())

    body = f"""
    <div class=\"section\">
        <h2>Analytics</h2>
        <p>Total Users: {total_users}</p>
        <p>Total Products: {total_products}</p>
        <p>Total Orders: {total_orders}</p>
        <p>Total Revenue: ${total_revenue:.2f}</p>
    </div>
    """

    return layout("Analytics", body)
