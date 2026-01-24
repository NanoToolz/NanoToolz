from web.routes.analytics import router as analytics_router
from web.routes.categories import router as categories_router
from web.routes.coupons import router as coupons_router
from web.routes.dashboard import router as dashboard_router
from web.routes.orders import router as orders_router
from web.routes.payments import router as payments_router
from web.routes.pricing import router as pricing_router
from web.routes.products import router as products_router
from web.routes.settings import router as settings_router
from web.routes.stock import router as stock_router
from web.routes.support import router as support_router
from web.routes.system import router as system_router
from web.routes.topups import router as topups_router
from web.routes.users import router as users_router

__all__ = [
    "analytics_router",
    "categories_router",
    "coupons_router",
    "dashboard_router",
    "orders_router",
    "payments_router",
    "pricing_router",
    "products_router",
    "settings_router",
    "stock_router",
    "support_router",
    "system_router",
    "topups_router",
    "users_router",
]
