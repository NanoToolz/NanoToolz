# ============================================
# MONGODB DATABASE WITH IMAGE STORAGE
# ============================================
# MongoDB Atlas + GridFS for images

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
from datetime import datetime
from bson import ObjectId

class MongoDB:
    """MongoDB Database with GridFS for images"""
    
    def __init__(self):
        # MongoDB Atlas connection
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "nanotoolz")
        
        # Initialize client
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client[self.db_name]
        
        # Collections
        self.users = self.db.users
        self.products = self.db.products
        self.orders = self.db.orders
        self.categories = self.db.categories
        self.settings = self.db.settings
        
        # GridFS for images
        self.fs = AsyncIOMotorGridFSBucket(self.db)
    
    # ============================================
    # USER OPERATIONS
    # ============================================
    
    async def get_user(self, user_id: int):
        """Get user by ID"""
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            # Create new user
            user = {
                "user_id": user_id,
                "balance": 0,
                "cart": {},
                "created_at": datetime.utcnow()
            }
            await self.users.insert_one(user)
        return user
    
    async def update_user(self, user_id: int, data: dict):
        """Update user data"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": data}
        )
    
    # ============================================
    # PRODUCT OPERATIONS
    # ============================================
    
    async def get_products(self, category_id: int = None):
        """Get all products or by category"""
        query = {"category_id": category_id} if category_id else {}
        products = await self.products.find(query).to_list(length=100)
        return products
    
    async def get_product(self, product_id: str):
        """Get product by ID"""
        return await self.products.find_one({"_id": ObjectId(product_id)})
    
    async def add_product(self, data: dict):
        """Add new product"""
        result = await self.products.insert_one(data)
        return str(result.inserted_id)
    
    async def update_product(self, product_id: str, data: dict):
        """Update product"""
        await self.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": data}
        )
    
    # ============================================
    # IMAGE OPERATIONS (GridFS)
    # ============================================
    
    async def save_image(self, file_data: bytes, filename: str):
        """Save image to GridFS"""
        file_id = await self.fs.upload_from_stream(
            filename,
            file_data,
            metadata={"uploaded_at": datetime.utcnow()}
        )
        return str(file_id)
    
    async def get_image(self, file_id: str):
        """Get image from GridFS"""
        grid_out = await self.fs.open_download_stream(ObjectId(file_id))
        contents = await grid_out.read()
        return contents
    
    async def delete_image(self, file_id: str):
        """Delete image from GridFS"""
        await self.fs.delete(ObjectId(file_id))
    
    # ============================================
    # ORDER OPERATIONS
    # ============================================
    
    async def create_order(self, data: dict):
        """Create new order"""
        data["created_at"] = datetime.utcnow()
        result = await self.orders.insert_one(data)
        return str(result.inserted_id)
    
    async def get_user_orders(self, user_id: int):
        """Get user's orders"""
        orders = await self.orders.find({"user_id": user_id}).sort("created_at", -1).to_list(length=50)
        return orders
    
    # ============================================
    # SETTINGS OPERATIONS
    # ============================================
    
    async def get_setting(self, key: str, default=None):
        """Get setting value"""
        setting = await self.settings.find_one({"key": key})
        return setting["value"] if setting else default
    
    async def set_setting(self, key: str, value):
        """Set setting value"""
        await self.settings.update_one(
            {"key": key},
            {"$set": {"value": value, "updated_at": datetime.utcnow()}},
            upsert=True
        )

# Create database instance
db = MongoDB()
