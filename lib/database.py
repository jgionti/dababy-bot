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

    def write(self, collection: str, name: str = "", data = {}):
        """Attempts to write a document into a collection.

        This function will try updating the data if a document of the
        same name already exists. Otherwise, a new document is added.
        """
        col = self.db[collection]
        if name != "":
            doc = {"_id" : name}
            doc.update(data)
        # Document exists in collection
        query = {"_id" : name}
        if col.find_one(query) is not None:
            doc = {"$set" : doc}
            col.update_one(query, doc)
        # Document must be inserted first
        else:
            col.insert_one(doc)

    def read(self, collection: str, name: str = "", query = {}):
        """Attempts to read data from a collection.

        Returns: Dict[name, value]
        """
        col = self.db[collection]
        if name != "":
            q = {"_id" : name}
            q.update(query)
        return col.find_one(q)

    def delete(self, collection: str, name: str = "", query = {}):
        col = self.db[collection]
        if name != "":
            q = {"_id" : name}
            q.update(query)
        return col.delete_one(q)

    # For future: can add write_many and read_many should the need arise
