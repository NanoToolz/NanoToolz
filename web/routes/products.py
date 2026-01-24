from html import escape

from fastapi import APIRouter, Depends, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.database.models import Category, Product
from src.services.pricing import set_product_pricing
from web.auth import verify_admin, security
from web.routes.helpers import parse_float, parse_int
from web.routes.utils import layout

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/products", response_class=HTMLResponse)
async def products_page(credentials=Depends(security), db: Session = Depends(get_db)):
    verify_admin(credentials)
    categories = db.query(Category).order_by(Category.name.asc()).all()
    products = db.query(Product).order_by(Product.id.desc()).all()

    options = "".join(
        f"<option value=\"{c.id}\">{escape(c.name)}</option>" for c in categories
    )

    body = f"""
    <div class=\"section\">
        <h2>Add Product</h2>
        <form method=\"post\" action=\"/admin/products/create\" enctype=\"multipart/form-data\">
            <label>Name</label>
            <input name=\"name\" required />
            <label>Category</label>
            <select name=\"category_id\">{options}</select>
            <label>Description</label>
            <textarea name=\"description\"></textarea>
            <label>Initial Price USD</label>
            <input name=\"initial_price_usd\" required />
            <label>Drop Period (days)</label>
            <input name=\"drop_period_days\" value=\"30\" />
            <label>Minimum Price USD</label>
            <input name=\"minimum_price_usd\" required />
            <label>Product Type</label>
            <input name=\"product_type\" value=\"file\" />
            <label>Stock (blank = unlimited)</label>
            <input name=\"stock\" />
            <label>Status</label>
            <select name=\"status\">
                <option value=\"published\">published</option>
                <option value=\"draft\">draft</option>
                <option value=\"archived\">archived</option>
            </select>
            <label>Image URL</label>
            <input name=\"image_url\" />
            <label>Upload Image</label>
            <input type=\"file\" name=\"image_file\" accept=\"image/*\" />
            <label>Affiliate Commission (%)</label>
            <input name=\"affiliate_commission\" value=\"0\" />
            <button class=\"btn btn-primary\" type=\"submit\">Create</button>
        </form>
    </div>
    <div class=\"section\">
        <h2>Products</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Category</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th>Stock</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """

    for product in products:
        category_name = product.category.name if product.category else "-"
        body += f"""
            <tr>
                <td>{product.id}</td>
                <td>{escape(product.name)}</td>
                <td>{escape(category_name)}</td>
                <td>${float(product.price_usd or 0):.2f}</td>
                <td>{escape(product.status)}</td>
                <td>{product.stock if product.stock is not None else "∞"}</td>
                <td>
                    <a class=\"btn btn-secondary\" href=\"/admin/products/{product.id}\">Edit</a>
                    <form class=\"inline\" method=\"post\" action=\"/admin/products/{product.id}/delete\">
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

    return layout("Products", body)


@router.post("/products/create")
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(""),
    initial_price_usd: str = Form("0"),
    drop_period_days: str = Form("30"),
    minimum_price_usd: str = Form("0"),
    product_type: str = Form("file"),
    stock: str = Form(""),
    status: str = Form("published"),
    image_url: str = Form(""),
    image_file: UploadFile | None = File(None),
    affiliate_commission: str = Form("0"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)

    if image_file and image_file.filename:
        import os
        from datetime import datetime

        ext = os.path.splitext(image_file.filename)[1]
        filename = f"{datetime.utcnow().timestamp():.0f}{ext}"
        upload_path = os.path.join("web", "static", "uploads", filename)
        with open(upload_path, "wb") as buffer:
            buffer.write(await image_file.read())
        image_url = f"/static/uploads/{filename}"

    product = Product(
        name=name,
        category_id=category_id,
        description=description,
        product_type=product_type,
        stock=parse_int(stock, 0) if stock.strip() else None,
        status=status,
        image_url=image_url,
        affiliate_commission=parse_float(affiliate_commission, 0.0),
    )
    db.add(product)
    db.flush()

    set_product_pricing(
        db,
        product.id,
        parse_float(initial_price_usd, 0.0),
        parse_int(drop_period_days, 30),
        parse_float(minimum_price_usd, 0.0),
    )

    return RedirectResponse("/admin/products", status_code=303)


@router.get("/products/{product_id}", response_class=HTMLResponse)
async def product_edit_page(
    product_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return layout("Product Not Found", "<p>Product not found.</p>")
    categories = db.query(Category).order_by(Category.name.asc()).all()

    options = "".join(
        f"<option value=\"{c.id}\" {'selected' if product.category_id == c.id else ''}>{escape(c.name)}</option>"
        for c in categories
    )

    body = f"""
    <div class=\"section\">
        <h2>Edit Product #{product.id}</h2>
        <form method=\"post\" action=\"/admin/products/{product.id}/update\" enctype=\"multipart/form-data\">
            <label>Name</label>
            <input name=\"name\" value=\"{escape(product.name)}\" required />
            <label>Category</label>
            <select name=\"category_id\">{options}</select>
            <label>Description</label>
            <textarea name=\"description\">{escape(product.description or '')}</textarea>
            <label>Initial Price USD</label>
            <input name=\"initial_price_usd\" value=\"{float(product.price_initial_usd or product.price_usd or 0):.2f}\" />
            <label>Drop Period (days)</label>
            <input name=\"drop_period_days\" value=\"{product.drop_period_days}\" />
            <label>Minimum Price USD</label>
            <input name=\"minimum_price_usd\" value=\"{float(product.price_minimum_usd or 0):.2f}\" />
            <label>Product Type</label>
            <input name=\"product_type\" value=\"{escape(product.product_type or '')}\" />
            <label>Stock (blank = unlimited)</label>
            <input name=\"stock\" value=\"{'' if product.stock is None else product.stock}\" />
            <label>Status</label>
            <select name=\"status\">
                <option value=\"published\" {'selected' if product.status == 'published' else ''}>published</option>
                <option value=\"draft\" {'selected' if product.status == 'draft' else ''}>draft</option>
                <option value=\"archived\" {'selected' if product.status == 'archived' else ''}>archived</option>
            </select>
            <label>Image URL</label>
            <input name=\"image_url\" value=\"{escape(product.image_url or '')}\" />
            <label>Upload Image</label>
            <input type=\"file\" name=\"image_file\" accept=\"image/*\" />
            <label>Affiliate Commission (%)</label>
            <input name=\"affiliate_commission\" value=\"{float(product.affiliate_commission or 0):.2f}\" />
            <button class=\"btn btn-primary\" type=\"submit\">Save</button>
            <a class=\"btn btn-secondary\" href=\"/admin/products\">Back</a>
        </form>
    </div>
    """

    return layout("Edit Product", body)


@router.post("/products/{product_id}/update")
async def update_product(
    product_id: int,
    name: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(""),
    initial_price_usd: str = Form("0"),
    drop_period_days: str = Form("30"),
    minimum_price_usd: str = Form("0"),
    product_type: str = Form("file"),
    stock: str = Form(""),
    status: str = Form("published"),
    image_url: str = Form(""),
    image_file: UploadFile | None = File(None),
    affiliate_commission: str = Form("0"),
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)

    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        if image_file and image_file.filename:
            import os
            from datetime import datetime

            ext = os.path.splitext(image_file.filename)[1]
            filename = f"{datetime.utcnow().timestamp():.0f}{ext}"
            upload_path = os.path.join("web", "static", "uploads", filename)
            with open(upload_path, "wb") as buffer:
                buffer.write(await image_file.read())
            image_url = f"/static/uploads/{filename}"

        product.name = name
        product.category_id = category_id
        product.description = description
        product.product_type = product_type
        product.stock = parse_int(stock, 0) if stock.strip() else None
        product.status = status
        product.image_url = image_url
        product.affiliate_commission = parse_float(affiliate_commission, 0.0)
        db.commit()

        set_product_pricing(
            db,
            product.id,
            parse_float(initial_price_usd, 0.0),
            parse_int(drop_period_days, 30),
            parse_float(minimum_price_usd, 0.0),
        )

    return RedirectResponse(f"/admin/products/{product_id}", status_code=303)


@router.post("/products/{product_id}/delete")
async def delete_product(
    product_id: int,
    credentials=Depends(security),
    db: Session = Depends(get_db),
):
    verify_admin(credentials)
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse("/admin/products", status_code=303)
