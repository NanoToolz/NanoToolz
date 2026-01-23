from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Payment, User
from src.services.pricing import convert_usdt_to_usd
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/topups", response_class=HTMLResponse)
async def topups_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    topups = (
        db.query(Payment)
        .filter(Payment.method.like("topup%"))
        .order_by(Payment.id.desc())
        .limit(200)
        .all()
    )

    body = """
    <div class=\"section\">
        <h2>Topups</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Amount</th><th>Status</th><th>Ref</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for payment in topups:
        body += f"""
            <tr>
                <td>{payment.id}</td>
                <td>{payment.user_id}</td>
                <td>{float(payment.amount or 0):.2f} {escape(payment.currency or '')}</td>
                <td>{escape(payment.status)}</td>
                <td>{escape(payment.payment_ref or '')}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/topups/{payment.id}/status\">
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
    return layout("Topups", body)


@router.post("/topups/{payment_id}/status")
async def update_topup_status(
    payment_id: int,
    status: str = Form("pending"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        return RedirectResponse("/admin/topups", status_code=303)

    if status == "confirmed" and payment.status != "confirmed":
        amount = float(payment.amount or 0)
        currency = (payment.currency or "").upper()
        credit_amount = convert_usdt_to_usd(amount) if currency == "USDT" else amount
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            user.credits = float(user.credits) + credit_amount
        payment.status = "confirmed"
        db.commit()
        return RedirectResponse("/admin/topups", status_code=303)

    payment.status = status
    db.commit()
    return RedirectResponse("/admin/topups", status_code=303)
