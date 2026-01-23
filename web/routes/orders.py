from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Order
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders", response_class=HTMLResponse)
async def orders_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    orders = db.query(Order).order_by(Order.id.desc()).limit(200).all()

    body = """
    <div class=\"section\">
        <h2>Orders</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Product</th><th>Amount</th><th>Payment</th><th>Delivery</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for order in orders:
        if order.user:
            user_name = order.user.username or str(order.user.telegram_id)
        else:
            user_name = "-"
        product_name = order.product.name if order.product else "-"
        body += f"""
            <tr>
                <td>{order.id}</td>
                <td>{escape(user_name)}</td>
                <td>{escape(product_name)}</td>
                <td>${float(order.price_paid_usd or 0):.2f}</td>
                <td>{escape(order.payment_status)}</td>
                <td>{escape(order.delivery_status)}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/orders/{order.id}/status\">
                        <select name=\"payment_status\">
                            <option value=\"pending\" {'selected' if order.payment_status == 'pending' else ''}>pending</option>
                            <option value=\"completed\" {'selected' if order.payment_status == 'completed' else ''}>completed</option>
                            <option value=\"failed\" {'selected' if order.payment_status == 'failed' else ''}>failed</option>
                        </select>
                        <select name=\"delivery_status\">
                            <option value=\"pending\" {'selected' if order.delivery_status == 'pending' else ''}>pending</option>
                            <option value=\"sent\" {'selected' if order.delivery_status == 'sent' else ''}>sent</option>
                            <option value=\"failed\" {'selected' if order.delivery_status == 'failed' else ''}>failed</option>
                        </select>
                        <button class=\"btn btn-primary\" type=\"submit\">Update</button>
                    </form>
                </td>
            </tr>
        """
    body += """
            </tbody>
        </table>
    </div>
    """
    return layout("Orders", body)


@router.post("/orders/{order_id}/status")
async def orders_update_status(
    order_id: int,
    payment_status: str = Form("pending"),
    delivery_status: str = Form("pending"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.payment_status = payment_status
        order.delivery_status = delivery_status
        db.commit()
    return RedirectResponse("/admin/orders", status_code=303)
