from html import escape
from datetime import datetime

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Coupon
from web.auth import verify_admin, security
from web.routes.helpers import parse_float, parse_int
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/coupons", response_class=HTMLResponse)
async def coupons_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    coupons = db.query(Coupon).order_by(Coupon.id.desc()).all()

    body = """
    <div class=\"section\">
        <h2>Create Coupon</h2>
        <form method=\"post\" action=\"/admin/coupons/create\">
            <label>Code</label>
            <input name=\"code\" required />
            <label>Discount Type</label>
            <select name=\"discount_type\">
                <option value=\"percent\">percent</option>
                <option value=\"fixed\">fixed</option>
            </select>
            <label>Value</label>
            <input name=\"value\" value=\"0\" />
            <label>Usage Limit (0 = unlimited)</label>
            <input name=\"usage_limit\" value=\"0\" />
            <label>Expires At (YYYY-MM-DD)</label>
            <input name=\"expires_at\" />
            <label>Active</label>
            <select name=\"active\">
                <option value=\"true\">true</option>
                <option value=\"false\">false</option>
            </select>
            <button class=\"btn btn-primary\" type=\"submit\">Create</button>
        </form>
    </div>
    <div class=\"section\">
        <h2>Coupons</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Code</th><th>Type</th><th>Value</th><th>Usage</th><th>Active</th><th>Expires</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """

    for coupon in coupons:
        usage = f"{coupon.used_count}/{coupon.usage_limit or '∞'}"
        expires = coupon.expires_at.strftime("%Y-%m-%d") if coupon.expires_at else "-"
        body += f"""
            <tr>
                <td>{coupon.id}</td>
                <td>{escape(coupon.code)}</td>
                <td>{escape(coupon.discount_type)}</td>
                <td>{float(coupon.value):.2f}</td>
                <td>{usage}</td>
                <td>{'Yes' if coupon.active else 'No'}</td>
                <td>{expires}</td>
                <td>
                    <a class=\"btn btn-secondary\" href=\"/admin/coupons/{coupon.id}\">Edit</a>
                    <form class=\"inline\" method=\"post\" action=\"/admin/coupons/{coupon.id}/delete\">
                        <button class=\"btn btn-danger\" type=\"submit\">Delete</button>
                    </form>
                </td>
            </tr>
        """

    body += """
            </tbody>
        </table>
    </div>
    """

    return layout("Coupons", body)


@router.post("/coupons/create")
async def create_coupon(
    code: str = Form(...),
    discount_type: str = Form("percent"),
    value: str = Form("0"),
    usage_limit: str = Form("0"),
    expires_at: str = Form(""),
    active: str = Form("true"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    expiry = None
    if expires_at.strip():
        try:
            expiry = datetime.strptime(expires_at.strip(), "%Y-%m-%d")
        except ValueError:
            expiry = None
    coupon = Coupon(
        code=code.strip().upper(),
        discount_type=discount_type,
        value=parse_float(value, 0.0),
        usage_limit=parse_int(usage_limit, 0),
        active=active == "true",
        expires_at=expiry,
    )
    db.add(coupon)
    db.commit()
    return RedirectResponse("/admin/coupons", status_code=303)


@router.get("/coupons/{coupon_id}", response_class=HTMLResponse)
async def coupon_edit_page(
    coupon_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if not coupon:
        return layout("Coupon Not Found", "<p>Coupon not found.</p>")

    expires = coupon.expires_at.strftime("%Y-%m-%d") if coupon.expires_at else ""
    body = f"""
    <div class=\"section\">
        <h2>Edit Coupon #{coupon.id}</h2>
        <form method=\"post\" action=\"/admin/coupons/{coupon.id}/update\">
            <label>Code</label>
            <input name=\"code\" value=\"{escape(coupon.code)}\" required />
            <label>Discount Type</label>
            <select name=\"discount_type\">
                <option value=\"percent\" {'selected' if coupon.discount_type == 'percent' else ''}>percent</option>
                <option value=\"fixed\" {'selected' if coupon.discount_type == 'fixed' else ''}>fixed</option>
            </select>
            <label>Value</label>
            <input name=\"value\" value=\"{float(coupon.value):.2f}\" />
            <label>Usage Limit</label>
            <input name=\"usage_limit\" value=\"{coupon.usage_limit}\" />
            <label>Used Count</label>
            <input name=\"used_count\" value=\"{coupon.used_count}\" />
            <label>Expires At</label>
            <input name=\"expires_at\" value=\"{expires}\" />
            <label>Active</label>
            <select name=\"active\">
                <option value=\"true\" {'selected' if coupon.active else ''}>true</option>
                <option value=\"false\" {'selected' if not coupon.active else ''}>false</option>
            </select>
            <button class=\"btn btn-primary\" type=\"submit\">Save</button>
            <a class=\"btn btn-secondary\" href=\"/admin/coupons\">Back</a>
        </form>
    </div>
    """

    return layout("Edit Coupon", body)


@router.post("/coupons/{coupon_id}/update")
async def update_coupon(
    coupon_id: int,
    code: str = Form(...),
    discount_type: str = Form("percent"),
    value: str = Form("0"),
    usage_limit: str = Form("0"),
    used_count: str = Form("0"),
    expires_at: str = Form(""),
    active: str = Form("true"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if coupon:
        coupon.code = code.strip().upper()
        coupon.discount_type = discount_type
        coupon.value = parse_float(value, float(coupon.value))
        coupon.usage_limit = parse_int(usage_limit, coupon.usage_limit)
        coupon.used_count = parse_int(used_count, coupon.used_count)
        coupon.active = active == "true"
        if expires_at.strip():
            try:
                coupon.expires_at = datetime.strptime(expires_at.strip(), "%Y-%m-%d")
            except ValueError:
                pass
        else:
            coupon.expires_at = None
        db.commit()
    return RedirectResponse(f"/admin/coupons/{coupon_id}", status_code=303)


@router.post("/coupons/{coupon_id}/delete")
async def delete_coupon(
    coupon_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    coupon = db.query(Coupon).filter(Coupon.id == coupon_id).first()
    if coupon:
        db.delete(coupon)
        db.commit()
    return RedirectResponse("/admin/coupons", status_code=303)