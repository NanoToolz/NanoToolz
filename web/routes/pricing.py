from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Product
from src.services.pricing import get_price_display_info, set_product_pricing
from web.auth import verify_admin, security
from web.routes.helpers import parse_float, parse_int
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    products = db.query(Product).order_by(Product.id.desc()).all()

    body = """
    <div class=\"section\">
        <h2>Update Pricing</h2>
        <form method=\"post\" action=\"/admin/pricing/update\">
            <label>Product</label>
            <select name=\"product_id\">
    """
    for product in products:
        body += f"<option value=\"{product.id}\">{escape(product.name)}</option>"
    body += """
            </select>
            <label>Initial Price USD</label>
            <input name=\"initial_price_usd\" required />
            <label>Drop Period (days)</label>
            <input name=\"drop_period_days\" value=\"30\" />
            <label>Minimum Price USD</label>
            <input name=\"minimum_price_usd\" required />
            <button class=\"btn btn-primary\" type=\"submit\">Apply</button>
        </form>
    </div>
    <div class=\"section\">
        <h2>Current Pricing</h2>
        <table>
            <thead>
                <tr><th>Product</th><th>Current</th><th>Initial</th><th>Minimum</th><th>Status</th></tr>
            </thead>
            <tbody>
    """
    for product in products:
        info = get_price_display_info(product)
        body += (
            f"<tr><td>{escape(product.name)}</td>"
            f"<td>${info['current_price_usd']:.2f}</td>"
            f"<td>${info['initial_price_usd']:.2f}</td>"
            f"<td>${info['minimum_price_usd']:.2f}</td>"
            f"<td>{escape(info['status'])}</td></tr>"
        )
    body += """
            </tbody>
        </table>
    </div>
    """

    return layout("Pricing", body)


@router.post("/pricing/update")
async def pricing_update(
    product_id: int = Form(...),
    initial_price_usd: str = Form("0"),
    drop_period_days: str = Form("30"),
    minimum_price_usd: str = Form("0"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    set_product_pricing(
        db,
        product_id,
        parse_float(initial_price_usd, 0.0),
        parse_int(drop_period_days, 30),
        parse_float(minimum_price_usd, 0.0),
    )
    return RedirectResponse("/admin/pricing", status_code=303)
