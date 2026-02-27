from argparse import ArgumentParser, Namespace

from providers import AsyncBaseLLMClient
import asyncio
from dotenv import load_dotenv
from providers.ProviderFactory import ProviderFactory

async def main(args: Namespace) -> None:
    client: AsyncBaseLLMClient = ProviderFactory.from_model(
        model_name=args.model,
        instructions=args.system_prompt,
    )
    while True:
        query: str = await asyncio.to_thread(input, "> ")
        if query.lower() == "exit":
            return
        await client.generate_response(query=query)



if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--model", default="gpt-5.2")
    parser.add_argument("--system-prompt", default="you are a generic chat-bot with access to tools")
    load_dotenv()
    args: Namespace = parser.parse_args()
    asyncio.run(main(args))
