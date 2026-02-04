import random
import string
from datetime import datetime
from typing import Optional
from supabase import create_client, Client
from src.config import settings


def get_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def generate_referral_code() -> str:
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


class Database:
    def __init__(self):
        self.client = get_client()

    def get_user(self, user_id: int) -> Optional[dict]:
        result = self.client.table("users").select("*").eq("id", user_id).maybe_single().execute()
        return result.data

    def create_user(self, user_id: int, username: str = None, first_name: str = None, referred_by: int = None) -> dict:
        referral_code = generate_referral_code()
        data = {
            "id": user_id,
            "username": username,
            "first_name": first_name,
            "balance": 0.0,
            "tier": "bronze",
            "total_spent": 0.0,
            "referral_code": referral_code,
            "referred_by": referred_by,
            "referral_earnings": 0.0
        }
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else data

    def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> dict:
        user = self.get_user(user_id)
        if not user:
            user = self.create_user(user_id, username, first_name)
        return user

    def update_user(self, user_id: int, data: dict) -> dict:
        result = self.client.table("users").update(data).eq("id", user_id).execute()
        return result.data[0] if result.data else None

    def get_user_by_referral_code(self, code: str) -> Optional[dict]:
        result = self.client.table("users").select("*").eq("referral_code", code).maybe_single().execute()
        return result.data

    def add_balance(self, user_id: int, amount: float, description: str = None, tx_type: str = "topup") -> float:
        user = self.get_user(user_id)
        new_balance = float(user["balance"]) + amount
        self.update_user(user_id, {"balance": new_balance})
        self.client.table("transactions").insert({
            "user_id": user_id,
            "type": tx_type,
            "amount": amount,
            "description": description
        }).execute()
        return new_balance

    def deduct_balance(self, user_id: int, amount: float, description: str = None) -> float:
        user = self.get_user(user_id)
        new_balance = float(user["balance"]) - amount
        self.update_user(user_id, {"balance": new_balance})
        self.client.table("transactions").insert({
            "user_id": user_id,
            "type": "purchase",
            "amount": -amount,
            "description": description
        }).execute()
        return new_balance

    def update_user_tier(self, user_id: int) -> str:
        user = self.get_user(user_id)
        total_spent = float(user["total_spent"])
        new_tier = "bronze"
        for tier, threshold in sorted(settings.TIER_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
            if total_spent >= threshold:
                new_tier = tier
                break
        if new_tier != user["tier"]:
            self.update_user(user_id, {"tier": new_tier})
        return new_tier

    def get_categories(self) -> list:
        result = self.client.table("categories").select("*").eq("is_active", True).order("sort_order").execute()
        return result.data or []

    def get_category(self, category_id: int) -> Optional[dict]:
        result = self.client.table("categories").select("*").eq("id", category_id).maybe_single().execute()
        return result.data

    def create_category(self, name: str, emoji: str = "📦", description: str = None) -> dict:
        data = {"name": name, "emoji": emoji, "description": description}
        result = self.client.table("categories").insert(data).execute()
        return result.data[0] if result.data else None

    def update_category(self, category_id: int, data: dict) -> dict:
        result = self.client.table("categories").update(data).eq("id", category_id).execute()
        return result.data[0] if result.data else None

    def delete_category(self, category_id: int) -> bool:
        self.client.table("categories").update({"is_active": False}).eq("id", category_id).execute()
        return True

    def get_products(self, category_id: int = None) -> list:
        query = self.client.table("products").select("*").eq("is_active", True)
        if category_id:
            query = query.eq("category_id", category_id)
        result = query.order("id").execute()
        return result.data or []

    def get_product(self, product_id: int) -> Optional[dict]:
        result = self.client.table("products").select("*").eq("id", product_id).maybe_single().execute()
        return result.data

    def create_product(self, category_id: int, name: str, price: float, description: str = None, image_url: str = None) -> dict:
        data = {
            "category_id": category_id,
            "name": name,
            "price": price,
            "description": description,
            "image_url": image_url
        }
        result = self.client.table("products").insert(data).execute()
        return result.data[0] if result.data else None

    def update_product(self, product_id: int, data: dict) -> dict:
        result = self.client.table("products").update(data).eq("id", product_id).execute()
        return result.data[0] if result.data else None

    def delete_product(self, product_id: int) -> bool:
        self.client.table("products").update({"is_active": False}).eq("id", product_id).execute()
        return True

    def search_products(self, query: str) -> list:
        result = self.client.table("products").select("*").eq("is_active", True).ilike("name", f"%{query}%").execute()
        return result.data or []

    def get_stock_count(self, product_id: int) -> int:
        result = self.client.table("stock").select("id", count="exact").eq("product_id", product_id).eq("is_sold", False).execute()
        return result.count or 0

    def get_available_stock(self, product_id: int, quantity: int = 1) -> list:
        result = self.client.table("stock").select("*").eq("product_id", product_id).eq("is_sold", False).limit(quantity).execute()
        return result.data or []

    def add_stock(self, product_id: int, items: list) -> int:
        data = [{"product_id": product_id, "data": item} for item in items]
        result = self.client.table("stock").insert(data).execute()
        return len(result.data) if result.data else 0

    def mark_stock_sold(self, stock_ids: list, user_id: int) -> bool:
        self.client.table("stock").update({
            "is_sold": True,
            "sold_to": user_id,
            "sold_at": datetime.utcnow().isoformat()
        }).in_("id", stock_ids).execute()
        return True

    def get_cart(self, user_id: int) -> list:
        result = self.client.table("cart").select("*, products(*)").eq("user_id", user_id).execute()
        return result.data or []

    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> dict:
        existing = self.client.table("cart").select("*").eq("user_id", user_id).eq("product_id", product_id).maybe_single().execute()
        if existing.data:
            new_qty = existing.data["quantity"] + quantity
            result = self.client.table("cart").update({"quantity": new_qty}).eq("id", existing.data["id"]).execute()
            return result.data[0] if result.data else None
        else:
            result = self.client.table("cart").insert({
                "user_id": user_id,
                "product_id": product_id,
                "quantity": quantity
            }).execute()
            return result.data[0] if result.data else None

    def update_cart_quantity(self, user_id: int, product_id: int, quantity: int) -> bool:
        if quantity <= 0:
            self.client.table("cart").delete().eq("user_id", user_id).eq("product_id", product_id).execute()
        else:
            self.client.table("cart").update({"quantity": quantity}).eq("user_id", user_id).eq("product_id", product_id).execute()
        return True

    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        self.client.table("cart").delete().eq("user_id", user_id).eq("product_id", product_id).execute()
        return True

    def clear_cart(self, user_id: int) -> bool:
        self.client.table("cart").delete().eq("user_id", user_id).execute()
        return True

    def get_cart_total(self, user_id: int) -> float:
        cart = self.get_cart(user_id)
        total = 0.0
        for item in cart:
            if item.get("products"):
                total += float(item["products"]["price"]) * item["quantity"]
        return total

    def create_order(self, user_id: int, total: float, discount: float = 0, coupon_code: str = None, payment_method: str = "balance") -> dict:
        data = {
            "user_id": user_id,
            "total": total,
            "discount_applied": discount,
            "coupon_code": coupon_code,
            "status": "completed",
            "payment_method": payment_method
        }
        result = self.client.table("orders").insert(data).execute()
        return result.data[0] if result.data else None

    def add_order_item(self, order_id: int, product_id: int, stock_id: int, price: float, quantity: int = 1) -> dict:
        data = {
            "order_id": order_id,
            "product_id": product_id,
            "stock_id": stock_id,
            "price": price,
            "quantity": quantity
        }
        result = self.client.table("order_items").insert(data).execute()
        return result.data[0] if result.data else None

    def get_user_orders(self, user_id: int, limit: int = 10) -> list:
        result = self.client.table("orders").select("*, order_items(*, products(*), stock(*))").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data or []

    def get_order(self, order_id: int) -> Optional[dict]:
        result = self.client.table("orders").select("*, order_items(*, products(*), stock(*))").eq("id", order_id).maybe_single().execute()
        return result.data

    def get_coupon(self, code: str) -> Optional[dict]:
        result = self.client.table("coupons").select("*").eq("code", code.upper()).eq("is_active", True).maybe_single().execute()
        return result.data

    def validate_coupon(self, code: str, cart_total: float) -> tuple:
        coupon = self.get_coupon(code)
        if not coupon:
            return None, "Invalid coupon code"
        if coupon["max_uses"] and coupon["used_count"] >= coupon["max_uses"]:
            return None, "Coupon has reached maximum uses"
        if coupon["expires_at"]:
            expires = datetime.fromisoformat(coupon["expires_at"].replace("Z", "+00:00"))
            if datetime.now(expires.tzinfo) > expires:
                return None, "Coupon has expired"
        if coupon["min_purchase"] and cart_total < float(coupon["min_purchase"]):
            return None, f"Minimum purchase ${coupon['min_purchase']:.2f} required"
        return coupon, None

    def use_coupon(self, code: str) -> bool:
        coupon = self.get_coupon(code)
        if coupon:
            self.client.table("coupons").update({"used_count": coupon["used_count"] + 1}).eq("id", coupon["id"]).execute()
            return True
        return False

    def calculate_discount(self, coupon: dict, total: float) -> float:
        if coupon["discount_percent"]:
            return total * (coupon["discount_percent"] / 100)
        elif coupon["discount_amount"]:
            return min(float(coupon["discount_amount"]), total)
        return 0

    def create_coupon(self, code: str, discount_percent: int = None, discount_amount: float = None, min_purchase: float = 0, max_uses: int = None, expires_at: str = None) -> dict:
        data = {
            "code": code.upper(),
            "discount_percent": discount_percent,
            "discount_amount": discount_amount,
            "min_purchase": min_purchase,
            "max_uses": max_uses,
            "expires_at": expires_at
        }
        result = self.client.table("coupons").insert(data).execute()
        return result.data[0] if result.data else None

    def get_wishlist(self, user_id: int) -> list:
        result = self.client.table("wishlist").select("*, products(*)").eq("user_id", user_id).execute()
        return result.data or []

    def add_to_wishlist(self, user_id: int, product_id: int) -> bool:
        try:
            self.client.table("wishlist").insert({
                "user_id": user_id,
                "product_id": product_id
            }).execute()
            return True
        except Exception:
            return False

    def remove_from_wishlist(self, user_id: int, product_id: int) -> bool:
        self.client.table("wishlist").delete().eq("user_id", user_id).eq("product_id", product_id).execute()
        return True

    def is_in_wishlist(self, user_id: int, product_id: int) -> bool:
        result = self.client.table("wishlist").select("id").eq("user_id", user_id).eq("product_id", product_id).maybe_single().execute()
        return result.data is not None

    def create_ticket(self, user_id: int, subject: str) -> dict:
        data = {"user_id": user_id, "subject": subject, "status": "open"}
        result = self.client.table("support_tickets").insert(data).execute()
        return result.data[0] if result.data else None

    def get_user_tickets(self, user_id: int) -> list:
        result = self.client.table("support_tickets").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return result.data or []

    def get_ticket(self, ticket_id: int) -> Optional[dict]:
        result = self.client.table("support_tickets").select("*, ticket_messages(*)").eq("id", ticket_id).maybe_single().execute()
        return result.data

    def get_open_tickets(self) -> list:
        result = self.client.table("support_tickets").select("*, users(username, first_name)").in_("status", ["open", "in_progress"]).order("created_at").execute()
        return result.data or []

    def update_ticket_status(self, ticket_id: int, status: str) -> bool:
        self.client.table("support_tickets").update({"status": status, "updated_at": datetime.utcnow().isoformat()}).eq("id", ticket_id).execute()
        return True

    def add_ticket_message(self, ticket_id: int, user_id: int, message: str, is_admin: bool = False) -> dict:
        data = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "message": message,
            "is_admin": is_admin
        }
        result = self.client.table("ticket_messages").insert(data).execute()
        self.client.table("support_tickets").update({"updated_at": datetime.utcnow().isoformat()}).eq("id", ticket_id).execute()
        return result.data[0] if result.data else None

    def get_setting(self, key: str) -> Optional[str]:
        result = self.client.table("settings").select("value").eq("key", key).maybe_single().execute()
        return result.data["value"] if result.data else None

    def set_setting(self, key: str, value: str) -> bool:
        self.client.table("settings").upsert({
            "key": key,
            "value": value,
            "updated_at": datetime.utcnow().isoformat()
        }).execute()
        return True

    def get_referral_stats(self, user_id: int) -> dict:
        result = self.client.table("users").select("id", count="exact").eq("referred_by", user_id).execute()
        user = self.get_user(user_id)
        return {
            "referral_count": result.count or 0,
            "referral_earnings": float(user["referral_earnings"]) if user else 0,
            "referral_code": user["referral_code"] if user else None
        }

    def process_referral_commission(self, referred_user_id: int, purchase_amount: float) -> float:
        user = self.get_user(referred_user_id)
        if not user or not user["referred_by"]:
            return 0
        commission = purchase_amount * (settings.REFERRAL_COMMISSION / 100)
        referrer = self.get_user(user["referred_by"])
        if referrer:
            new_earnings = float(referrer["referral_earnings"]) + commission
            new_balance = float(referrer["balance"]) + commission
            self.update_user(referrer["id"], {
                "referral_earnings": new_earnings,
                "balance": new_balance
            })
            self.client.table("transactions").insert({
                "user_id": referrer["id"],
                "type": "referral",
                "amount": commission,
                "description": f"Commission from referral purchase"
            }).execute()
        return commission

    def get_stats(self) -> dict:
        users = self.client.table("users").select("id", count="exact").execute()
        orders = self.client.table("orders").select("id", count="exact").eq("status", "completed").execute()
        revenue = self.client.table("orders").select("total").eq("status", "completed").execute()
        total_revenue = sum(float(o["total"]) for o in (revenue.data or []))
        products = self.client.table("products").select("id", count="exact").eq("is_active", True).execute()
        stock = self.client.table("stock").select("id", count="exact").eq("is_sold", False).execute()
        return {
            "total_users": users.count or 0,
            "total_orders": orders.count or 0,
            "total_revenue": total_revenue,
            "total_products": products.count or 0,
            "total_stock": stock.count or 0
        }

    def get_transactions(self, user_id: int, limit: int = 10) -> list:
        result = self.client.table("transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return result.data or []


db = Database()
