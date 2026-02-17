from client.OpenAIClient import AsyncOpenAIClient
import asyncio
from dotenv import load_dotenv

async def main():
    client: AsyncOpenAIClient = AsyncOpenAIClient(
        model="gpt-5.2",
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
