from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Category, Order, Product, User
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", response_class=HTMLResponse)
async def dashboard(
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_revenue = sum(float(o.price_paid_usd or 0) for o in db.query(Order).all())

    recent_orders = db.query(Order).order_by(Order.id.desc()).limit(10).all()

    body = f"""
    <div class=\"grid\">
        <div class=\"card\"><h3>Products</h3><div class=\"value\">{total_products}</div></div>
        <div class=\"card\"><h3>Categories</h3><div class=\"value\">{total_categories}</div></div>
        <div class=\"card\"><h3>Users</h3><div class=\"value\">{total_users}</div></div>
        <div class=\"card\"><h3>Orders</h3><div class=\"value\">{total_orders}</div></div>
        <div class=\"card\"><h3>Revenue</h3><div class=\"value\">${total_revenue:.2f}</div></div>
    </div>
    <div class=\"section\">
        <h2>Recent Orders</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Product</th><th>Amount</th><th>Status</th></tr>
            </thead>
            <tbody>
    """
    for order in recent_orders:
        if order.user:
            user_name = order.user.username or str(order.user.telegram_id)
        else:
            user_name = "-"
        product_name = order.product.name if order.product else "-"
        body += (
            f"<tr><td>{order.id}</td><td>{user_name}</td>"
            f"<td>{product_name}</td><td>${float(order.price_paid_usd or 0):.2f}</td>"
            f"<td>{order.payment_status}</td></tr>"
        )

    body += """
            </tbody>
        </table>
    </div>
    """

    return layout("Admin Dashboard", body)
