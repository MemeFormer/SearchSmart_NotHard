from pymongo import MongoClient

class MongoDBClient:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["cli_assistant_db"]
        self.collection = self.db["search_results"]

    def insert_document(self, document):
        return self.collection.insert_one(document)

    def find_documents(self, query):
        return list(self.collection.find(query))