from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from src.database import get_db, init_db
from src.database.models import Product, Category, User, Order
from src.config import settings

app = FastAPI(title="NanoToolz Admin Panel", version="1.0.0")

# Initialize DB on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Dashboard - HTML endpoint
@app.get("/", response_class=HTMLResponse)
async def dashboard(db: Session = Depends(get_db)):
    """Admin dashboard home"""
    total_products = db.query(Product).count()
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_revenue = sum([o.price_paid_usd or 0 for o in db.query(Order).all()])
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NanoToolz Admin Dashboard</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; }}
            .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
            .container {{ max-width: 1200px; margin: 20px auto; padding: 0 20px; }}
            .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .metric-card h3 {{ color: #667eea; margin-bottom: 10px; }}
            .metric-card .value {{ font-size: 2em; font-weight: bold; color: #333; }}
            .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .section h2 {{ margin-bottom: 15px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #f9f9f9; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #ddd; }}
            td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
            tr:hover {{ background: #f9f9f9; }}
            .btn {{ padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }}
            .btn-primary {{ background: #667eea; color: white; }}
            .btn-primary:hover {{ background: #5568d3; }}
            .status-badge {{ padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
            .status-published {{ background: #d4edda; color: #155724; }}
            .status-draft {{ background: #fff3cd; color: #856404; }}
            nav {{ background: white; padding: 15px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            nav a {{ margin-right: 20px; text-decoration: none; color: #667eea; font-weight: 600; }}
            nav a:hover {{ color: #764ba2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛍️ NanoToolz Admin Dashboard</h1>
            <p>Premium Digital Products Store</p>
        </div>
        
        <div class="container">
            <nav>
                <a href="/">📊 Dashboard</a>
                <a href="/products">📦 Products</a>
                <a href="/categories">📂 Categories</a>
                <a href="/users">👥 Users</a>
                <a href="/orders">💰 Orders</a>
                <a href="/settings">⚙️ Settings</a>
            </nav>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>📦 Products</h3>
                    <div class="value">{total_products}</div>
                </div>
                <div class="metric-card">
                    <h3>👥 Users</h3>
                    <div class="value">{total_users}</div>
                </div>
                <div class="metric-card">
                    <h3>💰 Orders</h3>
                    <div class="value">{total_orders}</div>
                </div>
                <div class="metric-card">
                    <h3>💵 Revenue</h3>
                    <div class="value">${total_revenue:.2f}</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Recent Orders</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>User</th>
                            <th>Product</th>
                            <th>Amount (USD)</th>
                            <th>Status</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="6" style="text-align: center;">No orders yet</td></tr>
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>Top Products</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Price (USD)</th>
                            <th>Sales</th>
                            <th>Rating</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    top_products = db.query(Product).order_by(Product.sales_count.desc()).limit(10).all()
    for product in top_products:
        status_badge = f'<span class="status-badge status-{product.status}">{product.status.upper()}</span>'
        html += f"""
                        <tr>
                            <td>{product.name}</td>
                            <td>{product.category.name}</td>
                            <td>${product.price_usd}</td>
                            <td>{product.sales_count}</td>
                            <td>⭐ {product.rating}/5</td>
                            <td>{status_badge}</td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return html

# API Endpoints
@app.get("/api/products")
async def get_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
    return [{
        "id": p.id,
        "name": p.name,
        "category": p.category.name,
        "price": float(p.price_usd),
        "stock": p.stock,
        "sales": p.sales_count,
        "rating": p.rating,
        "status": p.status
    } for p in products]

@app.get("/api/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return [{
        "id": c.id,
        "name": c.name,
        "products_count": len(c.products)
    } for c in categories]

@app.get("/api/users")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return [{
        "id": u.id,
        "telegram_id": u.telegram_id,
        "username": u.username,
        "credits": float(u.credits),
        "orders": len(u.orders),
        "joined": u.created_at.isoformat()
    } for u in users]

@app.get("/api/orders")
async def get_orders(db: Session = Depends(get_db)):
    """Get all orders"""
    orders = db.query(Order).all()
    return [{
        "id": o.id,
        "user": o.user.username or f"User {o.user.telegram_id}",
        "product": o.product.name,
        "amount": float(o.price_paid_usd),
        "status": o.payment_status,
        "created": o.created_at.isoformat()
    } for o in orders]

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get business statistics"""
    products = db.query(Product).count()
    users = db.query(User).count()
    orders = db.query(Order).count()
    revenue = sum([o.price_paid_usd or 0 for o in db.query(Order).all()])
    
    return {
        "total_products": products,
        "total_users": users,
        "total_orders": orders,
        "total_revenue": float(revenue),
        "average_order_value": float(revenue / orders) if orders > 0 else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
