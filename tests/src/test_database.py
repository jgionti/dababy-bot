import uuid

import pytest

from src.database import Database

TEST_COLLECTION = "TEST_COLLECTION"


@pytest.fixture(scope="session")
def database():
    """Create a Database instance and clean up when the test session ends."""
    db = Database()

    yield db

    db.db.drop_collection(TEST_COLLECTION)


@pytest.fixture(autouse=True)
def clean_collection(database):
    """Ensure each test starts with an empty collection."""
    database.db.drop_collection(TEST_COLLECTION)
    yield
    database.db.drop_collection(TEST_COLLECTION)


@pytest.fixture
def doc_id():
    """Generate a unique document ID for each test."""
    return str(uuid.uuid4())


@pytest.fixture
def sample_document(database, doc_id):
    """Insert a sample document for tests that require one."""
    database.write(
        TEST_COLLECTION,
        doc_id,
        {
            "name": "Alice",
            "score": 10,
        },
    )

    return doc_id


class TestDatabase:
    def test_init(self, database):
        assert database is not None
        assert database.db is not None

    def test_write_new_document(self, database, doc_id):
        database.write(
            TEST_COLLECTION,
            doc_id,
            {
                "name": "Bob",
                "score": 5,
            },
        )

        doc = database.read(TEST_COLLECTION, doc_id)

        assert doc is not None
        assert doc["_id"] == doc_id
        assert doc["name"] == "Bob"
        assert doc["score"] == 5

    def test_write_updates_existing(self, database, doc_id):
        database.write(
            TEST_COLLECTION,
            doc_id,
            {
                "name": "Alice",
                "score": 10,
            },
        )

        database.write(
            TEST_COLLECTION,
            doc_id,
            {
                "name": "Charlie",
                "score": 42,
            },
        )

        doc = database.read(TEST_COLLECTION, doc_id)

        assert doc is not None
        assert doc["name"] == "Charlie"
        assert doc["score"] == 42

    def test_read_existing_field(self, database, sample_document):
        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "score",
        )

        assert value == 10

    def test_read_missing_field(self, database, sample_document):
        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "missing_field",
        )

        assert value is None

    def test_update_existing_field(self, database, sample_document):
        database.update_field(
            TEST_COLLECTION,
            sample_document,
            "score",
            25,
        )

        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "score",
        )

        assert value == 25

    def test_update_new_field(self, database, sample_document):
        database.update_field(
            TEST_COLLECTION,
            sample_document,
            "level",
            7,
        )

        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "level",
        )

        assert value == 7

    def test_increment_existing_field(self, database, sample_document):
        database.add_to_field(
            TEST_COLLECTION,
            sample_document,
            "score",
            5,
        )

        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "score",
        )

        assert value == 15

    def test_increment_new_field(self, database, sample_document):
        database.add_to_field(
            TEST_COLLECTION,
            sample_document,
            "coins",
            3,
        )

        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "coins",
        )

        assert value == 3

    def test_delete_existing_document(self, database, sample_document):
        result = database.delete(
            TEST_COLLECTION,
            sample_document,
        )

        assert result.acknowledged
        assert result.deleted_count == 1

        doc = database.read(
            TEST_COLLECTION,
            sample_document,
        )

        assert doc is None

    def test_delete_missing_document(self, database, doc_id):
        result = database.delete(
            TEST_COLLECTION,
            doc_id,
        )

        assert result.acknowledged
        assert result.deleted_count == 0

    def test_read_deleted_document(self, database, sample_document):
        database.delete(
            TEST_COLLECTION,
            sample_document,
        )

        value = database.read_field(
            TEST_COLLECTION,
            sample_document,
            "score",
        )

        assert value is None

    def test_update_missing_document(self, database, doc_id):
        database.update_field(
            TEST_COLLECTION,
            doc_id,
            "score",
            99,
        )

        doc = database.read(
            TEST_COLLECTION,
            doc_id,
        )

        assert doc is None

    def test_read_many(self, database):
        for i in range(5):
            database.write(
                TEST_COLLECTION,
                f"user-{i}",
                {
                    "value": i,
                },
            )

        docs = database.read_many(TEST_COLLECTION)

        assert len(docs) == 5
        assert all("value" in doc for doc in docs)

    def test_update_raw(self, database, sample_document):
        database.update_raw(
            TEST_COLLECTION,
            sample_document,
            {
                "$set": {
                    "score": 100,
                    "rank": "gold",
                }
            },
        )

        doc = database.read(
            TEST_COLLECTION,
            sample_document,
        )

        assert doc["score"] == 100
        assert doc["rank"] == "gold"