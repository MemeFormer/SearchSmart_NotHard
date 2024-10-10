from tavily import Client as TavilyAPIClient

class TavilyClient:
    def __init__(self, api_key):
        self.client = TavilyAPIClient(
            api_key=api_key
        )


    def set_mongodb_collection(self, collection):
        self.client.collection = collection

    def search(self, query, save_foreign=False, search_depth="basic"):  # Corrected syntax
        self.client.save_foreign = save_foreign  # Correct placement of assignment
        return self.client.search(query, search_depth=search_depth)  # Removed semicolon and extra parenthesis