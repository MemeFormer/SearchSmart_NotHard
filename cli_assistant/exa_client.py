from exa_py import Exa

class ExaClient:
    def __init__(self, api_key):
        self.client = Exa(api_key)

    def search(self, query, num_results=5):
        return self.client.search(query, num_results=num_results)

    def get_contents(self, url):
        return self.client.get_contents(url)

    def find_similar(self, url, num_results=5):
        return self.client.find_similar(url, num_results=num_results)