import json
import os
import asyncio
import threading
from typing import Dict, List, Any, Optional
from copy import deepcopy

class JsonDatabase:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(JsonDatabase, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.data_dir = "data"
        self._ensure_dir()
        
        # File paths
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.products_file = os.path.join(self.data_dir, "products.json")
        self.categories_file = os.path.join(self.data_dir, "categories.json")
        self.orders_file = os.path.join(self.data_dir, "orders.json")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.stock_file = os.path.join(self.data_dir, "stock.json")
        self.coupons_file = os.path.join(self.data_dir, "coupons.json")

        self._load_all()
        self._initialized = True

    def _ensure_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_json(self, file_path: str, default: Any) -> Any:
        if not os.path.exists(file_path):
            self._save_json(file_path, default)
            return default
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"ERROR: Failed to load {file_path}: {e}. Using defaults.")
            return default

    def _save_json_sync(self, file_path: str, data: Any):
        """Synchronous atomic write (runs in thread pool)"""
        try:
            temp_path = f"{file_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, file_path)
        except (IOError, OSError) as e:
            print(f"ERROR: Failed to save {file_path}: {e}")
            # Attempt recovery by removing temp file
            try:
                os.remove(f"{file_path}.tmp")
            except:
                pass

    async def _save_json_async(self, file_path: str, data: Any):
        """Non-blocking async save using thread pool"""
        await asyncio.to_thread(self._save_json_sync, file_path, data)

    def _save_json(self, file_path: str, data: Any):
        """Legacy sync method - schedules async save if event loop running"""
        try:
            loop = asyncio.get_running_loop()
            # Schedule non-blocking save
            loop.create_task(self._save_json_async(file_path, data))
        except RuntimeError:
            # No event loop, use sync
            self._save_json_sync(file_path, data)

    def _load_all(self):
        self.users = self._load_json(self.users_file, {})
        self.products = self._load_json(self.products_file, [])
        self.categories = self._load_json(self.categories_file, [
            {"id": 1, "name": "Software", "emoji": "💻"},
            {"id": 2, "name": "Accounts", "emoji": "👤"},
            {"id": 3, "name": "Services", "emoji": "🛠️"}
        ])
        self.orders = self._load_json(self.orders_file, [])
        self.settings = self._load_json(self.settings_file, {
            "store_name": "NanoToolz",
            "support_username": "One_P_Man",
            "admin_ids": [],
            "maintenance": False
        })
        self.stock = self._load_json(self.stock_file, {})  # product_id -> [list of items]
        self.coupons = self._load_json(self.coupons_file, [])

    def save_users(self):
        self._save_json(self.users_file, self.users)

    def save_products(self):
        self._save_json(self.products_file, self.products)

    def save_categories(self):
        self._save_json(self.categories_file, self.categories)

    def save_orders(self):
        self._save_json(self.orders_file, self.orders)
        
    def save_settings(self):
        self._save_json(self.settings_file, self.settings)

    def save_stock(self):
        self._save_json(self.stock_file, self.stock)

    def save_coupons(self):
        self._save_json(self.coupons_file, self.coupons)

    # --- User Methods ---
    def get_user(self, user_id: int) -> dict:
        uid = str(user_id)
        if uid not in self.users:
            self.users[uid] = {
                "id": user_id,
                "balance": 0.0,
                "cart": {},  # product_id -> qty
                "orders": [],
                "joined_at": None
            }
            self.save_users()
        return self.users[uid]

    def update_user(self, user_id: int, data: dict):
        uid = str(user_id)
        if uid in self.users:
            self.users[uid].update(data)
            self.save_users()

    # --- Product Methods ---
    def get_products(self, category_id: int = None) -> List[dict]:
        if category_id:
            return [p for p in self.products if p.get("category_id") == category_id]
        return self.products

    def get_product(self, product_id: int) -> Optional[dict]:
        for p in self.products:
            if p["id"] == product_id:
                return p
        return None

    def add_product(self, product: dict):
        # Generate ID if missing
        if "id" not in product:
            product["id"] = max([p["id"] for p in self.products] or [0]) + 1
        self.products.append(product)
        self.save_products()
        return product["id"]
    
    def update_product(self, product_id: int, updates: dict):
        for p in self.products:
            if p["id"] == product_id:
                p.update(updates)
                self.save_products()
                return True
        return False
        
    def delete_product(self, product_id: int):
        self.products = [p for p in self.products if p["id"] != product_id]
        self.save_products()

    # --- Stock Methods ---
    def add_stock(self, product_id: int, items: List[str]):
        pid = str(product_id)
        if pid not in self.stock:
            self.stock[pid] = []
        self.stock[pid].extend(items)
        self.save_stock()

    def get_stock_count(self, product_id: int) -> int:
        return len(self.stock.get(str(product_id), []))

    def pop_stock(self, product_id: int, count: int) -> List[str]:
        """Atomically pop stock items with validation"""
        pid = str(product_id)
        if pid not in self.stock:
            return []
        
        # Validate sufficient stock before popping
        if len(self.stock[pid]) < count:
            return []  # Fail atomically - return empty list
        
        items = []
        for _ in range(count):
            items.append(self.stock[pid].pop(0))
        self.save_stock()
        return items

    # --- Order Methods ---
    def create_order(self, order_data: dict):
        if "id" not in order_data:
            order_data["id"] = len(self.orders) + 1
        self.orders.append(order_data)
        self.save_orders()
        return order_data["id"]

    # --- Category Methods ---
    def get_categories(self) -> List[dict]:
        return self.categories
    
    def get_category(self, cat_id: int) -> Optional[dict]:
        for c in self.categories:
            if c["id"] == cat_id:
                return c
        return None

db = JsonDatabase()