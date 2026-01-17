"""
Base repository module.

Provides abstract base class for all repository implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Generic

from motor.motor_asyncio import AsyncIOMotorCollection

from .connection import database


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository class.
    
    Provides common database operations for all repositories.
    All specific repositories should inherit from this class.
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize repository with collection name.
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self._collection_name = collection_name
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """
        Get MongoDB collection.
        
        Returns:
            AsyncIOMotorCollection: MongoDB collection instance
        """
        return database.get_collection(self._collection_name)
    
    async def create(self, data: dict[str, Any]) -> str:
        """
        Create a new document.
        
        Args:
            data: Document data
            
        Returns:
            str: Created document ID
        """
        # TODO: Insert document into collection
        # TODO: Return inserted ID
        pass
    
    async def find_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        """
        Find document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Optional[dict]: Document data or None if not found
        """
        # TODO: Find document by _id
        # TODO: Return document or None
        pass
    
    async def find_one(self, filter_query: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Find one document matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            Optional[dict]: Document data or None if not found
        """
        # TODO: Find one document matching filter
        # TODO: Return document or None
        pass
    
    async def find_many(
        self,
        filter_query: dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Find multiple documents matching the filter.
        
        Args:
            filter_query: MongoDB filter query
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            list[dict]: List of documents
        """
        # TODO: Find documents matching filter
        # TODO: Apply skip and limit
        # TODO: Return list of documents
        pass
    
    async def update(self, doc_id: str, data: dict[str, Any]) -> bool:
        """
        Update document by ID.
        
        Args:
            doc_id: Document ID
            data: Update data
            
        Returns:
            bool: True if document was updated, False otherwise
        """
        # TODO: Update document by _id
        # TODO: Return success status
        pass
    
    async def delete(self, doc_id: str) -> bool:
        """
        Delete document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            bool: True if document was deleted, False otherwise
        """
        # TODO: Delete document by _id
        # TODO: Return success status
        pass
    
    async def count(self, filter_query: dict[str, Any] = None) -> int:
        """
        Count documents matching the filter.
        
        Args:
            filter_query: MongoDB filter query (optional)
            
        Returns:
            int: Number of documents
        """
        # TODO: Count documents matching filter
        # TODO: Return count
        pass
