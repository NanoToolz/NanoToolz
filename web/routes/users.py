from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import User
from web.auth import verify_admin, security
from web.routes.helpers import parse_float
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_class=HTMLResponse)
async def users_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    users = db.query(User).order_by(User.id.desc()).limit(200).all()

    body = """
    <div class=\"section\">
        <h2>Users</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Telegram ID</th><th>Username</th><th>Credits</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for user in users:
        status = "BANNED" if user.is_banned else "ACTIVE"
        body += f"""
            <tr>
                <td>{user.id}</td>
                <td>{user.telegram_id}</td>
                <td>{escape(user.username or '-') }</td>
                <td>${float(user.credits):.2f}</td>
                <td>{status}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/users/{user.id}/toggle\">
                        <button class=\"btn btn-secondary\" type=\"submit\">{'Unban' if user.is_banned else 'Ban'}</button>
                    </form>
                    <form class=\"inline\" method=\"post\" action=\"/admin/users/{user.id}/credits\">
                        <input name=\"credits\" value=\"{float(user.credits):.2f}\" />
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
    return layout("Users", body)


@router.post("/users/{user_id}/toggle")
async def toggle_user(
    user_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_banned = not user.is_banned
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)


@router.post("/users/{user_id}/credits")
async def update_credits(
    user_id: int,
    credits: str = Form("0"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.credits = parse_float(credits, float(user.credits))
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)
