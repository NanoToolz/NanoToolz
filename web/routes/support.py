from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import SupportTicket
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/support", response_class=HTMLResponse)
async def support_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    tickets = db.query(SupportTicket).order_by(SupportTicket.id.desc()).limit(200).all()

    body = """
    <div class=\"section\">
        <h2>Support Tickets</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Category</th><th>Subject</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for ticket in tickets:
        user_name = ticket.user.username or str(ticket.user.telegram_id)
        body += f"""
            <tr>
                <td>{ticket.id}</td>
                <td>{escape(user_name)}</td>
                <td>{escape(ticket.category)}</td>
                <td>{escape(ticket.subject)}</td>
                <td>{escape(ticket.status)}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/support/{ticket.id}/status\">
                        <select name=\"status\">
                            <option value=\"open\" {'selected' if ticket.status == 'open' else ''}>open</option>
                            <option value=\"in_progress\" {'selected' if ticket.status == 'in_progress' else ''}>in_progress</option>
                            <option value=\"resolved\" {'selected' if ticket.status == 'resolved' else ''}>resolved</option>
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
    return layout("Support Tickets", body)


@router.post("/support/{ticket_id}/status")
async def support_update_status(
    ticket_id: int,
    status: str = Form("open"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if ticket:
        ticket.status = status
        db.commit()
    return RedirectResponse("/admin/support", status_code=303)
