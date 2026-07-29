import os
from typing import Any, Optional

import pymongo
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase
from pymongo.results import DeleteResult, UpdateResult


class Database:
    """Wrapper for MongoDB read/write operations.

    MongoDB hierarchy:
        Client -> Database -> Collection -> Document
    Each document has a _id used to identify itself.
    """

    COLLECTION_MEMBERS = "members"
    COLLECTION_EVENTS = "events"
    COLLECTION_GOLDEN_MOMENTS = "golden_moments"

    _client = pymongo.MongoClient(os.environ["MONGO_URL"])

    def __init__(self):
        self.db: MongoDatabase = self._client["main"]

    def _collection(self, name: str) -> Collection:
        return self.db[name]

    def write(
        self,
        collection: str,
        id: str,
        data: Optional[dict[str, Any]] = None,
    ) -> UpdateResult:
        """Insert or update a document.

        Uses MongoDB's upsert functionality so only one database
        operation is required.
        """
        return self._collection(collection).update_one(
            {"_id": id},
            {"$set": data or {}},
            upsert=True,
        )

    def read(
        self,
        collection: str,
        id: Optional[str] = None,
        query: Optional[dict[str, Any]] = None,
    ) -> Optional[dict]:
        """Read a single document."""
        q = query.copy() if query else {}

        if id is not None:
            q["_id"] = id

        return self._collection(collection).find_one(q)

    def delete(
        self,
        collection: str,
        id: Optional[str] = None,
        query: Optional[dict[str, Any]] = None,
    ) -> DeleteResult:
        """Delete a single document."""
        q = query.copy() if query else {}

        if id is not None:
            q["_id"] = id

        return self._collection(collection).delete_one(q)

    def read_field(
        self,
        collection: str,
        id: str,
        field: str,
    ) -> Any:
        """Read a single field from a document.

        Uses projection so MongoDB only returns the requested field.
        """
        doc = self._collection(collection).find_one(
            {"_id": id},
            {field: 1},
        )

        if doc is None:
            return None

        return doc.get(field)

    def update_field(
        self,
        collection: str,
        id: str,
        field: str,
        value: Any,
    ) -> UpdateResult:
        """Atomically update one field."""
        return self._collection(collection).update_one(
            {"_id": id},
            {"$set": {field: value}},
        )

    def add_to_field(
        self,
        collection: str,
        id: str,
        field: str,
        amount: int | float,
    ) -> UpdateResult:
        """Atomically increment a numeric field.

        Eliminates the previous read-modify-write sequence.
        """
        return self._collection(collection).update_one(
            {"_id": id},
            {"$inc": {field: amount}},
        )

    def update_raw(
        self,
        collection: str,
        id: str,
        payload: dict[str, Any],
        upsert: bool = True,
    ) -> UpdateResult:
        """Execute an arbitrary MongoDB update payload."""
        return self._collection(collection).update_one(
            {"_id": id},
            payload,
            upsert=upsert,
        )

    def read_many(
        self,
        collection: str,
        query: Optional[dict[str, Any]] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Read multiple documents."""
        return list(
            self._collection(collection)
            .find(query or {})
            .limit(limit)
        )