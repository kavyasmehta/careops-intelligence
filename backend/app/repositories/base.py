"""Generic MongoDB repository. Entity repositories subclass this and add
only what's actually entity-specific (custom filters, dedup checks, etc.)
instead of re-implementing CRUD + pagination each time.
"""
from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument

from app.core.errors import NotFoundError

__all__ = ["RepositoryBase", "NotFoundError"]


class RepositoryBase:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    @staticmethod
    def to_object_id(id_: str) -> ObjectId:
        try:
            return ObjectId(id_)
        except (InvalidId, TypeError) as exc:
            raise NotFoundError(id_) from exc

    @staticmethod
    def serialize(doc: dict) -> dict:
        doc = dict(doc)
        doc["id"] = str(doc.pop("_id"))
        return doc

    async def get(self, id_: str) -> dict | None:
        doc = await self.collection.find_one({"_id": self.to_object_id(id_)})
        return self.serialize(doc) if doc else None

    async def list(
        self,
        filter_: dict[str, Any],
        *,
        page: int,
        page_size: int,
        sort_field: str = "created_at",
        sort_direction: int = -1,
    ) -> tuple[list[dict], int]:
        total = await self.collection.count_documents(filter_)
        cursor = (
            self.collection.find(filter_)
            .sort(sort_field, sort_direction)
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        docs = [self.serialize(doc) async for doc in cursor]
        return docs, total

    async def create(self, data: dict[str, Any]) -> dict:
        now = datetime.now(UTC)
        payload = {**data, "created_at": now, "updated_at": now}
        result = await self.collection.insert_one(payload)
        doc = await self.collection.find_one({"_id": result.inserted_id})
        return self.serialize(doc)

    async def update(self, id_: str, data: dict[str, Any]) -> dict | None:
        payload = {**data, "updated_at": datetime.now(UTC)}
        doc = await self.collection.find_one_and_update(
            {"_id": self.to_object_id(id_)},
            {"$set": payload},
            return_document=ReturnDocument.AFTER,
        )
        return self.serialize(doc) if doc else None

    async def count(self, filter_: dict[str, Any]) -> int:
        return await self.collection.count_documents(filter_)
