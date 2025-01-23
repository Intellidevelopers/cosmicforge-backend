from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    _instance = None

    @staticmethod
    def get_instance():
        if Database._instance is None:
            Database()
        return Database._instance

    def __init__(self):
        if Database._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Database._instance = self
            self.client = None
            self.db = None
            self.connect()

    def connect(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client.get_database()
            self.client.admin.command('ismaster')
            logger.info("Successfully connected to the database")
        except ConnectionFailure:
            logger.error("Server not available")
            raise

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update)

    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def create_index(self, collection_name, keys, **kwargs):
        collection = self.get_collection(collection_name)
        return collection.create_index(keys, **kwargs)
