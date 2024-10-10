from typing import List, Dict, Any
import json
from dataclasses import asdict
class Assistant:
    def __init__(self, groq_client, tavily_client, exa_client, mongodb_client):
        self.groq_client = groq_client
        self.tavily_client = tavily_client
        self.exa_client = exa_client
        self.mongodb_client = mongodb_client

    def process_query(self, query: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful assistant with access to web search capabilities through Tavily and Exa APIs. Use these tools when necessary to provide accurate and up-to-date information."},
            {"role": "user", "content": query}
        ]
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "tavily_search",
                    "description": "Search the web using Tavily API with Hybrid RAG capabilities",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "search_depth": {
                                "type": "string",
                                "enum": ["basic", "advanced"],
                                "description": "The depth of the search"
                            },
                            "save_foreign": {
                                "type": "boolean",
                                "description": "Whether to insert new web data into the local database"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "exa_search",
                    "description": "Search the web using Exa API for precise content retrieval",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "The number of results to return"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "exa_get_contents",
                    "description": "Retrieve clean HTML content from a given URL using Exa API",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to retrieve content from"
                            }
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "exa_find_similar",
                    "description": "Find similar pages based on a given URL using Exa API",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to find similar pages for"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "The number of similar pages to return"
                            }
                        },
                        "required": ["url"]
                    }
                }
            }
        ]

        response = self.groq_client.chat_completion(
            model="mixtral-8x7b-32768",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=1000
        )

        assistant_message = response.choices[0].message

        api_used = None
        search_results = None

        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "tavily_search":
                    api_used = "Tavily"
                    search_results = self.tavily_client.search(**function_args)
                    # Convert SearchResponse to a dictionary
                    search_results = asdict(search_results) if hasattr(search_results, '__dict__') else search_results
                elif function_name == "exa_search":
                    api_used = "Exa"
                    search_results = self.exa_client.search(**function_args)
                    # Convert SearchResponse to a dictionary
                    search_results = asdict(search_results) if hasattr(search_results, '__dict__') else search_results
    

                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(search_results)
                })

            print(f"Assistant message: {assistant_message}")
            print(f"Assistant content: {assistant_message.content if hasattr(assistant_message, 'content') else None}")

            # Get a new response from the assistant based on the function results
            response = self.groq_client.chat_completion(
                model="mixtral-8x7b-32768",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

        return {
        "content": assistant_message.content if hasattr(assistant_message, 'content') else None,
        "api_used": api_used,
        "search_results": search_results,
        "query": query
    }