import os

import pymongo


class Database:
    """Class for read/write operations to the bot's database.

    This database uses MongoDB. 
    It follows the hierarchy: Client > Database > Collection > Document

    Each document has a _id used to identify itself.
    """
    def __init__(self):
        """Instantiates a Database class and creates a connection to
        the main database.
        """
        url = os.environ.get("MONGO_URL")
        client = pymongo.MongoClient(url)
        self.db = client["main"]

    def write(self, collection: str, id: str = "", data = {}):
        """Attempts to write a document into a collection.

        This function will try updating the data if a document of the
        same id already exists. Otherwise, a new document is added.
        """
        col = self.db[collection]
        if id != "":
            doc = {"_id" : id}
            doc.update(data)
        # Document exists in collection
        query = {"_id" : id}
        if col.find_one(query) is not None:
            doc = {"$set" : doc}
            col.update_one(query, doc)
        # Document must be inserted first
        else:
            col.insert_one(doc)

    def read(self, collection: str, id: str = "", query = {}):
        """Attempts to read data from a collection.

        Returns: Dict[id, value]
        """
        col = self.db[collection]
        if id != "":
            q = {"_id" : id}
            q.update(query)
        return col.find_one(q)

    def delete(self, collection: str, id: str = "", query = {}):
        """Attempts to delete data from a collection.
        
        Returns: DeleteResult
        """
        col = self.db[collection]
        if id != "":
            q = {"_id" : id}
            q.update(query)
        return col.delete_one(q)

    def read_field(self, collection: str, id: str, field: str):
        """Attempts to read a field from a document.

        Returns: Optional[Any]
        """
        d = self.read(collection, id)
        if d is not None and field in d:
            return d[field]
        return None
        
    def update_field(self, collection: str, id: str, field: str, value):
        """Attempts to update a field within a document.
        
        Does nothing if the document is not found.
        """
        d = self.read(collection, id)
        if d is not None:
            d[field] = value
            self.write(collection, id, d)

    def add_to_field(self, collection: str, id: str, field: str, add):
        """Attempts to add to a field within a document.
        
        Creates field if the field is not found.
        """
        val = self.read_field(collection, id, field)
        if val is None:
            self.update_field(collection, id, field, add)
        else:
            self.update_field(collection, id, field, val + add)

    # For future: can add write_many and read_many should the need arise
