from __future__ import annotations

import secrets
from html import escape
from typing import Optional

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from src.config import settings
from src.database import get_db, init_db
from src.database.models import (
    Category,
    Order,
    Payment,
    Product,
    ProductDelivery,
    Setting,
    SupportTicket,
    User,
)

app = FastAPI(title="NanoToolz Admin Panel", version="2.0.0")
security = HTTPBasic()


@app.on_event("startup")
async def startup_event() -> None:
    init_db()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    is_user = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    is_pass = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (is_user and is_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


def layout(title: str, body: str) -> HTMLResponse:
    css = """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f6f7fb; color: #222; }
        header { background: #0f172a; color: #fff; padding: 18px 24px; }
        header h1 { font-size: 20px; }
        nav { background: #fff; padding: 12px 24px; border-bottom: 1px solid #e2e8f0; }
        nav a { margin-right: 16px; color: #0f172a; text-decoration: none; font-weight: bold; }
        nav a:hover { color: #2563eb; }
        main { padding: 24px; }
        .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
        .card { background: #fff; padding: 16px; border-radius: 10px; border: 1px solid #e2e8f0; }
        .card h3 { font-size: 14px; color: #475569; margin-bottom: 6px; }
        .card .value { font-size: 24px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
        th { background: #f8fafc; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }
        form.inline { display: inline; }
        input, select, textarea { width: 100%; padding: 8px; margin: 6px 0; border: 1px solid #cbd5f5; border-radius: 6px; }
        textarea { min-height: 80px; }
        .btn { padding: 8px 14px; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .btn-primary { background: #2563eb; color: white; }
        .btn-danger { background: #dc2626; color: white; }
        .btn-secondary { background: #e2e8f0; }
        .section { background: #fff; padding: 18px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 18px; }
        .section h2 { margin-bottom: 12px; font-size: 18px; }
        .muted { color: #64748b; font-size: 13px; }
    </style>
    """
    nav = """
    <nav>
        <a href="/">Dashboard</a>
        <a href="/products">Products</a>
        <a href="/categories">Categories</a>
        <a href="/deliveries">Deliveries</a>
        <a href="/orders">Orders</a>
        <a href="/support">Support</a>
        <a href="/settings">Settings</a>
    </nav>
    """
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{escape(title)}</title>
        {css}
    </head>
    <body>
        <header>
            <h1>{escape(title)}</h1>
        </header>
        {nav}
        <main>{body}</main>
    </body>
    </html>
    """
    return HTMLResponse(html)


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int(value: str, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@app.get("/", response_class=HTMLResponse)
async def dashboard(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    total_products = db.query(Product).count()
    total_categories = db.query(Category).count()
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_revenue = sum(float(o.price_paid_usd or 0) for o in db.query(Order).all())
    pending_orders = db.query(Order).filter(Order.payment_status == "pending").count()
    body = f"""
    <div class="grid">
        <div class="card"><h3>Products</h3><div class="value">{total_products}</div></div>
        <div class="card"><h3>Categories</h3><div class="value">{total_categories}</div></div>
        <div class="card"><h3>Users</h3><div class="value">{total_users}</div></div>
        <div class="card"><h3>Orders</h3><div class="value">{total_orders}</div></div>
        <div class="card"><h3>Revenue</h3><div class="value">${total_revenue:.2f}</div></div>
        <div class="card"><h3>Pending Orders</h3><div class="value">{pending_orders}</div></div>
    </div>
    """
    return layout("NanoToolz Admin Dashboard", body)


@app.get("/products", response_class=HTMLResponse)
async def products_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    categories = db.query(Category).order_by(Category.name.asc()).all()
    products = db.query(Product).order_by(Product.id.desc()).all()
    options = """""".join(
        f"<option value=\"{c.id}\">{escape(c.name)}</option>" for c in categories
    )
    body = """
    <div class="section">
        <h2>Add Product</h2>
        <form method="post" action="/products/create">
            <label>Name</label>
            <input name="name" required />
            <label>Category</label>
            <select name="category_id">{options}</select>
            <label>Description</label>
            <textarea name="description"></textarea>
            <label>Price USD</label>
            <input name="price_usd" />
            <label>Price USDT</label>
            <input name="price_usdt" />
            <label>Product Type</label>
            <input name="product_type" placeholder="key, file, license" />
            <label>Stock (blank = unlimited)</label>
            <input name="stock" />
            <label>Status</label>
            <select name="status">
                <option value="published">published</option>
                <option value="draft">draft</option>
                <option value="archived">archived</option>
            </select>
            <label>Image URL</label>
            <input name="image_url" />
            <label>Affiliate Commission (%)</label>
            <input name="affiliate_commission" />
            <button class="btn btn-primary" type="submit">Create</button>
        </form>
    </div>
    <div class="section">
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
    """.format(options=options)
    for product in products:
        category_name = product.category.name if product.category else "-"
        body += f"""
            <tr>
                <td>{product.id}</td>
                <td>{escape(product.name)}</td>
                <td>{escape(category_name)}</td>
                <td>${float(product.price_usd):.2f}</td>
                <td>{escape(product.status)}</td>
                <td>{product.stock if product.stock is not None else "∞"}</td>
                <td>
                    <a class="btn btn-secondary" href="/products/{product.id}">Edit</a>
                    <form class="inline" method="post" action="/products/{product.id}/delete">
                        <button class="btn btn-danger" type="submit">Delete</button>
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


@app.post("/products/create")
async def create_product(
    name: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(""),
    price_usd: str = Form("0"),
    price_usdt: str = Form(""),
    product_type: str = Form("file"),
    stock: str = Form(""),
    status: str = Form("published"),
    image_url: str = Form(""),
    affiliate_commission: str = Form("0"),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    usd = parse_float(price_usd, 0.0)
    usdt = parse_float(price_usdt, usd)
    stock_value = parse_int(stock, None) if stock.strip() else None
    product = Product(
        name=name,
        category_id=category_id,
        description=description,
        price_usd=usd,
        price_usdt=usdt,
        product_type=product_type,
        stock=stock_value,
        status=status,
        image_url=image_url,
        affiliate_commission=parse_float(affiliate_commission, 0.0),
    )
    db.add(product)
    db.commit()
    return RedirectResponse("/products", status_code=303)


@app.get("/products/{product_id}", response_class=HTMLResponse)
async def product_edit_page(
    product_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return layout("Product Not Found", "<p>Product not found.</p>")
    categories = db.query(Category).order_by(Category.name.asc()).all()
    options = "".join(
        f"<option value=\"{c.id}\" {'selected' if product.category_id == c.id else ''}>{escape(c.name)}</option>"
        for c in categories
    )
    body = f"""
    <div class="section">
        <h2>Edit Product #{product.id}</h2>
        <form method="post" action="/products/{product.id}/update">
            <label>Name</label>
            <input name="name" value="{escape(product.name)}" required />
            <label>Category</label>
            <select name="category_id">{options}</select>
            <label>Description</label>
            <textarea name="description">{escape(product.description or '')}</textarea>
            <label>Price USD</label>
            <input name="price_usd" value="{float(product.price_usd):.2f}" />
            <label>Price USDT</label>
            <input name="price_usdt" value="{float(product.price_usdt):.2f}" />
            <label>Product Type</label>
            <input name="product_type" value="{escape(product.product_type or '')}" />
            <label>Stock (blank = unlimited)</label>
            <input name="stock" value="{'' if product.stock is None else product.stock}" />
            <label>Status</label>
            <select name="status">
                <option value="published" {'selected' if product.status == 'published' else ''}>published</option>
                <option value="draft" {'selected' if product.status == 'draft' else ''}>draft</option>
                <option value="archived" {'selected' if product.status == 'archived' else ''}>archived</option>
            </select>
            <label>Image URL</label>
            <input name="image_url" value="{escape(product.image_url or '')}" />
            <label>Affiliate Commission (%)</label>
            <input name="affiliate_commission" value="{float(product.affiliate_commission or 0):.2f}" />
            <button class="btn btn-primary" type="submit">Save</button>
            <a class="btn btn-secondary" href="/products">Back</a>
        </form>
    </div>
    """
    return layout("Edit Product", body)


@app.post("/products/{product_id}/update")
async def update_product(
    product_id: int,
    name: str = Form(...),
    category_id: int = Form(...),
    description: str = Form(""),
    price_usd: str = Form("0"),
    price_usdt: str = Form(""),
    product_type: str = Form("file"),
    stock: str = Form(""),
    status: str = Form("published"),
    image_url: str = Form(""),
    affiliate_commission: str = Form("0"),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.name = name
        product.category_id = category_id
        product.description = description
        product.price_usd = parse_float(price_usd, 0.0)
        product.price_usdt = parse_float(price_usdt, product.price_usd)
        product.product_type = product_type
        product.stock = parse_int(stock, None) if stock.strip() else None
        product.status = status
        product.image_url = image_url
        product.affiliate_commission = parse_float(affiliate_commission, 0.0)
        db.commit()
    return RedirectResponse(f"/products/{product_id}", status_code=303)


@app.post("/products/{product_id}/delete")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        db.delete(product)
        db.commit()
    return RedirectResponse("/products", status_code=303)


@app.get("/categories", response_class=HTMLResponse)
async def categories_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    categories = db.query(Category).order_by(Category.display_order.asc()).all()
    body = """
    <div class="section">
        <h2>Add Category</h2>
        <form method="post" action="/categories/create">
            <label>Name</label>
            <input name="name" required />
            <label>Emoji</label>
            <input name="emoji" value="📦" />
            <label>Description</label>
            <textarea name="description"></textarea>
            <label>Display Order</label>
            <input name="display_order" value="0" />
            <label>Featured</label>
            <select name="featured">
                <option value="false">No</option>
                <option value="true">Yes</option>
            </select>
            <button class="btn btn-primary" type="submit">Create</button>
        </form>
    </div>
    <div class="section">
        <h2>Categories</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Emoji</th><th>Featured</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for category in categories:
        body += f"""
            <tr>
                <td>{category.id}</td>
                <td>{escape(category.name)}</td>
                <td>{escape(category.emoji or '')}</td>
                <td>{'Yes' if category.featured else 'No'}</td>
                <td>
                    <a class="btn btn-secondary" href="/categories/{category.id}">Edit</a>
                    <form class="inline" method="post" action="/categories/{category.id}/delete">
                        <button class="btn btn-danger" type="submit">Delete</button>
                    </form>
                </td>
            </tr>
        """
    body += """
            </tbody>
        </table>
    </div>
    """
    return layout("Categories", body)


@app.post("/categories/create")
async def create_category(
    name: str = Form(...),
    emoji: str = Form("📦"),
    description: str = Form(""),
    display_order: str = Form("0"),
    featured: str = Form("false"),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    category = Category(
        name=name,
        emoji=emoji,
        description=description,
        display_order=parse_int(display_order, 0) or 0,
        featured=featured == "true",
    )
    db.add(category)
    db.commit()
    return RedirectResponse("/categories", status_code=303)


@app.get("/categories/{category_id}", response_class=HTMLResponse)
async def category_edit_page(
    category_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return layout("Category Not Found", "<p>Category not found.</p>")
    body = f"""
    <div class="section">
        <h2>Edit Category #{category.id}</h2>
        <form method="post" action="/categories/{category.id}/update">
            <label>Name</label>
            <input name="name" value="{escape(category.name)}" required />
            <label>Emoji</label>
            <input name="emoji" value="{escape(category.emoji or '')}" />
            <label>Description</label>
            <textarea name="description">{escape(category.description or '')}</textarea>
            <label>Display Order</label>
            <input name="display_order" value="{category.display_order}" />
            <label>Featured</label>
            <select name="featured">
                <option value="false" {'selected' if not category.featured else ''}>No</option>
                <option value="true" {'selected' if category.featured else ''}>Yes</option>
            </select>
            <button class="btn btn-primary" type="submit">Save</button>
            <a class="btn btn-secondary" href="/categories">Back</a>
        </form>
    </div>
    """
    return layout("Edit Category", body)


@app.post("/categories/{category_id}/update")
async def update_category(
    category_id: int,
    name: str = Form(...),
    emoji: str = Form("📦"),
    description: str = Form(""),
    display_order: str = Form("0"),
    featured: str = Form("false"),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        category.name = name
        category.emoji = emoji
        category.description = description
        category.display_order = parse_int(display_order, 0) or 0
        category.featured = featured == "true"
        db.commit()
    return RedirectResponse(f"/categories/{category_id}", status_code=303)


@app.post("/categories/{category_id}/delete")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category:
        db.delete(category)
        db.commit()
    return RedirectResponse("/categories", status_code=303)


@app.get("/deliveries", response_class=HTMLResponse)
async def deliveries_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    products = db.query(Product).order_by(Product.name.asc()).all()
    deliveries = db.query(ProductDelivery).order_by(ProductDelivery.id.desc()).limit(200).all()
    options = "".join(
        f"<option value=\"{p.id}\">{escape(p.name)}</option>" for p in products
    )
    body = f"""
    <div class="section">
        <h2>Add Delivery</h2>
        <form method="post" action="/deliveries/create">
            <label>Product</label>
            <select name="product_id">{options}</select>
            <label>Delivery Content (key/link/text)</label>
            <textarea name="delivery_content"></textarea>
            <button class="btn btn-primary" type="submit">Add Delivery</button>
        </form>
    </div>
    <div class="section">
        <h2>Latest Deliveries</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>Product</th><th>Content</th><th>Used</th><th>Actions</th></tr>
            </thead>
            <tbody>
    """
    for delivery in deliveries:
        body += f"""
            <tr>
                <td>{delivery.id}</td>
                <td>{escape(delivery.product.name if delivery.product else '-') }</td>
                <td class="muted">{escape((delivery.delivery_content or '')[:60])}</td>
                <td>{'Yes' if delivery.used else 'No'}</td>
                <td>
                    <form class="inline" method="post" action="/deliveries/{delivery.id}/delete">
                        <button class="btn btn-danger" type="submit">Delete</button>
                    </form>
                </td>
            </tr>
        """
    body += """
            </tbody>
        </table>
    </div>
    """
    return layout("Deliveries", body)


@app.post("/deliveries/create")
async def deliveries_create(
    product_id: int = Form(...),
    delivery_content: str = Form(""),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    delivery = ProductDelivery(
        product_id=product_id,
        delivery_content=delivery_content,
        used=False,
    )
    db.add(delivery)
    db.commit()
    return RedirectResponse("/deliveries", status_code=303)


@app.post("/deliveries/{delivery_id}/delete")
async def deliveries_delete(
    delivery_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    delivery = db.query(ProductDelivery).filter(ProductDelivery.id == delivery_id).first()
    if delivery:
        db.delete(delivery)
        db.commit()
    return RedirectResponse("/deliveries", status_code=303)


@app.get("/orders", response_class=HTMLResponse)
async def orders_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    orders = db.query(Order).order_by(Order.id.desc()).limit(200).all()
    body = """
    <div class="section">
        <h2>Orders</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>User</th>
                    <th>Product</th>
                    <th>Amount</th>
                    <th>Payment</th>
                    <th>Delivery</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    """
    for order in orders:
        body += f"""
            <tr>
                <td>{order.id}</td>
                <td>{escape(order.user.username or str(order.user.telegram_id))}</td>
                <td>{escape(order.product.name if order.product else '-') }</td>
                <td>${float(order.price_paid_usd or 0):.2f}</td>
                <td>{escape(order.payment_status)}</td>
                <td>{escape(order.delivery_status)}</td>
                <td>
                    <form class="inline" method="post" action="/orders/{order.id}/status">
                        <select name="payment_status">
                            <option value="pending" {'selected' if order.payment_status == 'pending' else ''}>pending</option>
                            <option value="completed" {'selected' if order.payment_status == 'completed' else ''}>completed</option>
                            <option value="failed" {'selected' if order.payment_status == 'failed' else ''}>failed</option>
                        </select>
                        <select name="delivery_status">
                            <option value="pending" {'selected' if order.delivery_status == 'pending' else ''}>pending</option>
                            <option value="sent" {'selected' if order.delivery_status == 'sent' else ''}>sent</option>
                            <option value="failed" {'selected' if order.delivery_status == 'failed' else ''}>failed</option>
                        </select>
                        <button class="btn btn-primary" type="submit">Update</button>
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


@app.post("/orders/{order_id}/status")
async def orders_update_status(
    order_id: int,
    payment_status: str = Form("pending"),
    delivery_status: str = Form("pending"),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.payment_status = payment_status
        order.delivery_status = delivery_status
        db.commit()
    return RedirectResponse("/orders", status_code=303)


@app.get("/support", response_class=HTMLResponse)
async def support_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    tickets = db.query(SupportTicket).order_by(SupportTicket.id.desc()).limit(200).all()
    body = """
    <div class="section">
        <h2>Support Tickets</h2>
        <table>
            <thead>
                <tr><th>ID</th><th>User</th><th>Category</th><th>Subject</th><th>Status</th></tr>
            </thead>
            <tbody>
    """
    for ticket in tickets:
        body += f"""
            <tr>
                <td>{ticket.id}</td>
                <td>{escape(ticket.user.username or str(ticket.user.telegram_id))}</td>
                <td>{escape(ticket.category)}</td>
                <td>{escape(ticket.subject)}</td>
                <td>{escape(ticket.status)}</td>
            </tr>
        """
    body += """
            </tbody>
        </table>
    </div>
    """
    return layout("Support", body)


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    def fetch(key: str, default: str) -> str:
        item = db.query(Setting).filter(Setting.key == key).first()
        return item.value if item else default

    store_name = fetch("store_name", settings.STORE_NAME)
    support_contact = fetch("support_contact", settings.SUPPORT_CONTACT)
    wallet_tron = fetch("payment_usdt_tron_wallet", settings.PAYMENT_WALLET_TRON)
    wallet_ltc = fetch("payment_ltc_wallet", settings.PAYMENT_WALLET_LTC)
    payment_notice = fetch("payment_notice", "Send the exact amount and tap 'I Paid' after payment.")

    body = f"""
    <div class="section">
        <h2>Store Settings</h2>
        <form method="post" action="/settings/update">
            <label>Store Name</label>
            <input name="store_name" value="{escape(store_name)}" />
            <label>Support Contact</label>
            <input name="support_contact" value="{escape(support_contact)}" />
            <label>USDT (TRON) Wallet</label>
            <input name="wallet_tron" value="{escape(wallet_tron)}" />
            <label>Litecoin Wallet</label>
            <input name="wallet_ltc" value="{escape(wallet_ltc)}" />
            <label>Payment Notice</label>
            <textarea name="payment_notice">{escape(payment_notice)}</textarea>
            <button class="btn btn-primary" type="submit">Save</button>
        </form>
    </div>
    """
    return layout("Settings", body)


@app.post("/settings/update")
async def settings_update(
    store_name: str = Form("NanoToolz Store"),
    support_contact: str = Form("@YourSupport"),
    wallet_tron: str = Form(""),
    wallet_ltc: str = Form(""),
    payment_notice: str = Form(""),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    def upsert(key: str, value: str) -> None:
        item = db.query(Setting).filter(Setting.key == key).first()
        if item:
            item.value = value
        else:
            db.add(Setting(key=key, value=value))

    upsert("store_name", store_name)
    upsert("support_contact", support_contact)
    upsert("payment_usdt_tron_wallet", wallet_tron)
    upsert("payment_ltc_wallet", wallet_ltc)
    upsert("payment_notice", payment_notice)
    db.commit()
    return RedirectResponse("/settings", status_code=303)


@app.get("/api/products")
async def get_products(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category.name if p.category else None,
            "price": float(p.price_usd),
            "stock": p.stock,
            "sales": p.sales_count,
            "rating": p.rating,
            "status": p.status,
        }
        for p in products
    ]


@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    categories = db.query(Category).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "products_count": len(c.products),
        }
        for c in categories
    ]


@app.get("/api/users")
async def get_users(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "credits": float(u.credits),
            "orders": len(u.orders),
            "joined": u.created_at.isoformat(),
        }
        for u in users
    ]


@app.get("/api/orders")
async def get_orders(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    orders = db.query(Order).all()
    return [
        {
            "id": o.id,
            "user": o.user.username or f"User {o.user.telegram_id}",
            "product": o.product.name if o.product else "-",
            "amount": float(o.price_paid_usd or 0),
            "status": o.payment_status,
            "created": o.created_at.isoformat(),
        }
        for o in orders
    ]


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db), _: None = Depends(require_admin)):
    products = db.query(Product).count()
    users = db.query(User).count()
    orders = db.query(Order).count()
    revenue = sum(float(o.price_paid_usd or 0) for o in db.query(Order).all())
    return {
        "total_products": products,
        "total_users": users,
        "total_orders": orders,
        "total_revenue": float(revenue),
        "average_order_value": float(revenue / orders) if orders > 0 else 0,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
