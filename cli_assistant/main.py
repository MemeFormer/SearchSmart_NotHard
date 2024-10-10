import os
import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from .assistant import Assistant
from .tavily_client import TavilyClient
from .exa_client import ExaClient
from .groq_client import GroqClient
from .mongodb_client import MongoDBClient

load_dotenv()

app = typer.Typer()
console = Console()

@app.command()
def chat():
    """Start a chat session with the CLI assistant."""
    groq_client = GroqClient(os.getenv("GROQ_API_KEY"))
    tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))
    exa_client = ExaClient(os.getenv("EXA_API_KEY"))
    mongodb_client = MongoDBClient(os.getenv("MONGODB_URI"))
    
    assistant = Assistant(groq_client, tavily_client, exa_client, mongodb_client)
    
    console.print(Panel("Welcome to the CLI Assistant! Type 'exit' to end the conversation or 'compare' to compare API results.", title="CLI Assistant", expand=False))

    while True:
        user_input = typer.prompt("You")
        if user_input.lower() == "exit":
            break
        
        response = assistant.process_query(user_input)
        
        # Check if we have a valid response content
        if response["content"]:
            console.print(Panel(response["content"], title="Assistant", expand=False))
        else:
            console.print("The assistant couldn't generate a response.")

        if response["api_used"]:
            console.print(f"Search performed using {response['api_used']} API")
        
   
        if response["api_used"] and typer.confirm("Would you like to compare with the other API?"):
            other_api = "Exa" if response["api_used"] == "Tavily" else "Tavily"
            compare_response = assistant.process_query(f"Use the {other_api} API to search for the same query")
    
        if compare_response["content"]:
            console.print(Panel(str(compare_response["content"]), title=f"Comparison ({other_api})", expand=False))
        else:
            console.print(f"No comparison results available from {other_api}")

        console.print("\nComparison of search results:")
        console.print(f"{response['api_used']} results:", response["search_results"])
        console.print(f"{other_api} results:", compare_response.get("search_results", "No results available"))


          
if __name__ == "__main__":
    app()