"""
MongoDB connection module.

Manages async MongoDB connection using Motor driver.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings


class Database:
    """
    Singleton database connection manager.
    
    Handles MongoDB connection lifecycle and provides access to database instance.
    """
    
    _instance: Optional["Database"] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls) -> "Database":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> None:
        """
        Establish connection to MongoDB.
        
        Creates Motor client and connects to the database specified in settings.
        """
        # TODO: Create Motor client with MongoDB URI
        # TODO: Get database instance
        # TODO: Test connection
        pass
    
    async def disconnect(self) -> None:
        """
        Close database connection.
        
        Properly closes MongoDB connection and cleans up resources.
        """
        # TODO: Close Motor client connection
        # TODO: Reset instance variables
        pass
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """
        Get database instance.
        
        Returns:
            AsyncIOMotorDatabase: MongoDB database instance
            
        Raises:
            RuntimeError: If database is not connected
        """
        # TODO: Check if database is connected
        # TODO: Return database instance
        pass
    
    def get_collection(self, name: str):
        """
        Get a collection from the database.
        
        Args:
            name: Collection name
            
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        # TODO: Return collection from database
        pass


# Global database instance
database = Database()
