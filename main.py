from client.AnthropicClient import AsyncAnthropicClient
import asyncio
from dotenv import load_dotenv

async def main():
    client: AsyncAnthropicClient = AsyncAnthropicClient(
        model="claude-opus-4-20250514",
        instructions="you are a generic chat-bot with access to tools",
    )
    while True:
        query: str = await asyncio.to_thread(input, "> ")
        if query.lower() == "exit":
            return
        await client.generate_response(query=query)



if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())
