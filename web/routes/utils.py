from html import escape
from fastapi.responses import HTMLResponse


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
        <a href="/admin">Dashboard</a>
        <a href="/admin/products">Products</a>
        <a href="/admin/pricing">Pricing</a>
        <a href="/admin/categories">Categories</a>
        <a href="/admin/users">Users</a>
        <a href="/admin/orders">Orders</a>
        <a href="/admin/payments">Payments</a>
        <a href="/admin/topups">Topups</a>
        <a href="/admin/settings">Settings</a>
        <a href="/admin/support">Support</a>
        <a href="/admin/analytics">Analytics</a>
        <a href="/admin/system">System</a>
    </nav>
    """
    html = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
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
