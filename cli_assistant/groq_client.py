from groq import Groq

class GroqClient:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def chat_completion(self, **kwargs):
        return self.client.chat.completions.create(**kwargs)