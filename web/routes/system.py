import os

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from src.database import get_db
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/system", response_class=HTMLResponse)
async def system_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    log_path = os.path.join("logs", "bot.log")
    log_exists = os.path.exists(log_path)
    body = f"""
    <div class=\"section\">
        <h2>System</h2>
        <p>Logs: {'Available' if log_exists else 'Not found'}</p>
        <p>Database: connected</p>
    </div>
    """
    return layout("System", body)
