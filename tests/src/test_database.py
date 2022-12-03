import pytest
from src.database import Database

TEST_COLLECTION = "TEST_COLLECTION"
ID = "_id"
TEST_ID = "TEST"
TEST_FIELD = "test"
TEST_FIELD_VAL = "data"
TEST_FIELD_VAL2 = "not data"
TEST_DATA = {TEST_FIELD : TEST_FIELD_VAL}

database = Database()

class TestDatabase:
    """Integration tests for Database class. Must execute all tests in order.

    If tests are executed out of order, unexpected behavior might occur.
    """

    @pytest.fixture(scope="session", autouse=True)
    def create_collection(self):
        """Helper: Create the test collection. Dropped when done."""
        if database.db.get_collection(TEST_COLLECTION) is None:
            database.db.create_collection(TEST_COLLECTION)
        yield
        database.db.drop_collection(TEST_COLLECTION)

    def check_data(self, data, id, field_val):
        assert data is not None
        assert data[ID] == id
        assert data[TEST_FIELD] == field_val

    def test_init(self):
        assert database is not None
        assert database.db is not None

    def test_write_read_new(self):
        """Write then read when document does not exist."""
        database.write(TEST_COLLECTION, TEST_ID, TEST_DATA)
        data = database.read(TEST_COLLECTION, TEST_ID)
        self.check_data(data, TEST_ID, TEST_FIELD_VAL)

    def test_write_read_exists(self):
        """Write then read when document already exists."""
        new_data = TEST_DATA
        new_data[TEST_FIELD] = TEST_FIELD_VAL2
        database.write(TEST_COLLECTION, TEST_ID, new_data)
        data = database.read(TEST_COLLECTION, TEST_ID)
        self.check_data(data, TEST_ID, TEST_FIELD_VAL2)

    def test_read_field_exists(self):
        """Tries to read an existing field from a document."""
        value = database.read_field(TEST_COLLECTION, TEST_ID, TEST_FIELD)
        assert value is not None
        assert value == TEST_FIELD_VAL2

    def test_read_field_fails(self):
        """Tries to read an nonexistent field from an existing document."""
        value = database.read_field(TEST_COLLECTION, TEST_ID, "chungus")
        assert value is None

    def test_update_field_exists(self):
        """Tries to update a field within a document."""
        new_value = TEST_FIELD_VAL
        database.update_field(TEST_COLLECTION, TEST_ID, TEST_FIELD, new_value)
        value = database.read_field(TEST_COLLECTION, TEST_ID, TEST_FIELD)
        assert value is not None
        assert value == TEST_FIELD_VAL

    def test_update_field_new(self):
        """Tries to update a field that needs to be added to the document."""
        new_field = "new_field"
        new_value = TEST_FIELD_VAL
        database.update_field(TEST_COLLECTION, TEST_ID, new_field, new_value)
        value = database.read_field(TEST_COLLECTION, TEST_ID, new_field)
        assert value is not None
        assert value == TEST_FIELD_VAL

    def test_add_to_field_exists(self):
        """Tries to add to a field within a document."""
        add_val = "!!!"
        expected = TEST_FIELD_VAL + add_val
        database.add_to_field(TEST_COLLECTION, TEST_ID, TEST_FIELD, add_val)
        value = database.read_field(TEST_COLLECTION, TEST_ID, TEST_FIELD)
        assert value is not None
        assert value == expected

    def test_add_to_field_exists(self):
        """Tries to add to a nonexistent field within a document."""
        new_field = "chungus"
        add_val = "!!!"
        database.add_to_field(TEST_COLLECTION, TEST_ID, new_field, add_val)
        value = database.read_field(TEST_COLLECTION, TEST_ID, new_field)
        assert value is not None
        assert value == add_val

    def test_delete_exists(self):
        """Deletes when document exists."""
        result = database.delete(TEST_COLLECTION, TEST_ID)
        assert result is not None
        assert result.acknowledged is True
        assert result.deleted_count > 0

    def test_delete_fail(self):
        """Tries to delete when document doesn't exist."""
        result = database.delete(TEST_COLLECTION, TEST_ID)
        assert result is not None
        assert result.acknowledged is True
        assert result.deleted_count == 0

    def test_read_field_deleted(self):
        """Tries to read a field from a nonexistent document."""
        data = database.read_field(TEST_COLLECTION, TEST_ID, TEST_FIELD)
        assert data is None

    def test_update_field_deleted(self):
        """Tries to update a field within a nonexistent document."""
        new_value = TEST_FIELD_VAL2
        database.update_field(TEST_COLLECTION, TEST_ID, TEST_FIELD, new_value)
        value = database.read_field(TEST_COLLECTION, TEST_ID, TEST_FIELD)
        assert value is None
