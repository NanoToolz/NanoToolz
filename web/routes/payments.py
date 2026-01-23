from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Payment, User
from src.services.orders import complete_payment, cancel_payment
from src.services.pricing import convert_usdt_to_usd
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/payments", response_class=HTMLResponse)
async def payments_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    payments = db.query(Payment).order_by(Payment.id.desc()).limit(200).all()

    body = """
    <div class=\"section\">
        <h2>Payments</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Method</th><th>Amount</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for payment in payments:
        body += f"""
            <tr>
                <td>{payment.id}</td>
                <td>{payment.user_id}</td>
                <td>{escape(payment.method or '-') }</td>
                <td>{float(payment.amount or 0):.2f} {escape(payment.currency or '')}</td>
                <td>{escape(payment.status)}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/payments/{payment.id}/status\">
                        <select name=\"status\">
                            <option value=\"pending\" {'selected' if payment.status == 'pending' else ''}>pending</option>
                            <option value=\"confirmed\" {'selected' if payment.status == 'confirmed' else ''}>confirmed</option>
                            <option value=\"failed\" {'selected' if payment.status == 'failed' else ''}>failed</option>
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
    return layout("Payments", body)


@router.post("/payments/{payment_id}/status")
async def update_payment_status(
    payment_id: int,
    status: str = Form("pending"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return RedirectResponse("/admin/payments", status_code=303)

    if status == "confirmed":
        if payment.status != "confirmed":
            if payment.method and payment.method.startswith("topup"):
                amount = float(payment.amount or 0)
                currency = (payment.currency or "").upper()
                credit_amount = (
                    convert_usdt_to_usd(amount) if currency == "USDT" else amount
                )
                user = db.query(User).filter(User.id == payment.user_id).first()
                if user:
                    user.credits = float(user.credits) + credit_amount
                payment.status = "confirmed"
                db.commit()
            elif payment.payment_ref:
                complete_payment(db, payment.payment_ref)
            else:
                payment.status = "confirmed"
                db.commit()
    elif status == "failed":
        if payment.status != "confirmed":
            if payment.payment_ref:
                cancel_payment(db, payment.payment_ref)
            else:
                payment.status = "failed"
                db.commit()
    else:
        payment.status = "pending"
        db.commit()
    return RedirectResponse("/admin/payments", status_code=303)
