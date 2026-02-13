from client.OpenAIClient import OpenAIClient
from tools.tools import registry
import asyncio
from dotenv import load_dotenv

async def main():
    client: OpenAIClient = OpenAIClient(
        model="gpt-5.2",
        instructions="you are a generic chat-bot with access to tools",
        tool_registry=registry
    )
    while True:
        query: str = await asyncio.to_thread(input, "> ")
        if query.lower() == "exit":
            return
        client.generate_response(query=query)



if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
