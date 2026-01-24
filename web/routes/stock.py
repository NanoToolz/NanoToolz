from html import escape

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Product, ProductDelivery
from web.auth import verify_admin, security
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stock", response_class=HTMLResponse)
async def stock_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    products = db.query(Product).order_by(Product.id.desc()).all()
    stock_items = db.query(ProductDelivery).order_by(ProductDelivery.id.desc()).limit(200).all()

    options = "".join(
        f"<option value=\"{p.id}\">{escape(p.name)}</option>" for p in products
    )

    body = f"""
    <div class=\"section\">
        <h2>Add Stock / Delivery Item</h2>
        <form method=\"post\" action=\"/admin/stock/create\">
            <label>Product</label>
            <select name=\"product_id\">{options}</select>
            <label>Delivery Content (key/link/credentials)</label>
            <textarea name=\"delivery_content\" required></textarea>
            <button class=\"btn btn-primary\" type=\"submit\">Add Stock</button>
        </form>
    </div>
    <div class=\"section\">
        <h2>Stock Items</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Product</th><th>Used</th><th>Content</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """

    for item in stock_items:
        product_name = item.product.name if item.product else "-"
        body += f"""
            <tr>
                <td>{item.id}</td>
                <td>{escape(product_name)}</td>
                <td>{'Yes' if item.used else 'No'}</td>
                <td>{escape((item.delivery_content or '')[:80])}</td>
                <td>
                    <form class=\"inline\" method=\"post\" action=\"/admin/stock/{item.id}/toggle\">
                        <button class=\"btn btn-secondary\" type=\"submit\">{'Mark Unused' if item.used else 'Mark Used'}</button>
                    </form>
                    <form class=\"inline\" method=\"post\" action=\"/admin/stock/{item.id}/delete\">
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

    return layout("Stock", body)


@router.post("/stock/create")
async def stock_create(
    product_id: int = Form(...),
    delivery_content: str = Form(...),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    item = ProductDelivery(product_id=product_id, delivery_content=delivery_content, used=False)
    db.add(item)
    db.commit()
    return RedirectResponse("/admin/stock", status_code=303)


@router.post("/stock/{item_id}/toggle")
async def stock_toggle(
    item_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    item = db.query(ProductDelivery).filter(ProductDelivery.id == item_id).first()
    if item:
        item.used = not item.used
        db.commit()
    return RedirectResponse("/admin/stock", status_code=303)


@router.post("/stock/{item_id}/delete")
async def stock_delete(
    item_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    item = db.query(ProductDelivery).filter(ProductDelivery.id == item_id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse("/admin/stock", status_code=303)