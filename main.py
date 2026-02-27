from argparse import ArgumentParser, Namespace

from providers import AsyncBaseLLMClient
import asyncio
from dotenv import load_dotenv
from providers.ProviderFactory import ProviderFactory
from providers.errors.ProviderError import (
    ProviderError,
    AuthenticationError,
    RateLimitExceededError,
    ModelNotFoundError,
    ConnectionError,
    ProviderApiError,
)


async def main(args: Namespace) -> None:
    try:
        client: AsyncBaseLLMClient = ProviderFactory.from_model(
            model_name=args.model,
            instructions=args.system_prompt,
        )
    except Exception as e:
        print(f"Failed to initialize provider for model '{args.model}': {e}")
        return

    print(f"Chat started with model '{args.model}'. Type 'exit' to quit.\n")

    while True:
        try:
            query: str = await asyncio.to_thread(input, "> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if query.strip().lower() == "exit":
            print("Goodbye!")
            return

        if not query.strip():
            continue

        try:
            await client.generate_response(query=query)
        except KeyboardInterrupt:
            print("\n[Interrupted]")
        except AuthenticationError as e:
            print(f"\n[Auth error] Check your API key: {e}")
        except RateLimitExceededError as e:
            print(f"\n[Rate limit] Try again in a moment: {e}")
        except ModelNotFoundError as e:
            print(f"\n[Model error] {e}")
        except ConnectionError as e:
            print(f"\n[Connection error] Could not reach the provider: {e}")
        except ProviderApiError as e:
            print(f"\n[API error] {e}")
        except ProviderError as e:
            print(f"\n[Provider error] {e}")
        except Exception as e:
            print(f"\n[Unexpected error] {type(e).__name__}: {e}")


if __name__ == "__main__":
    load_dotenv()
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--model", default="gpt-5.2")
    parser.add_argument("--system-prompt", default="you are a generic chat-bot with access to tools")
    args: Namespace = parser.parse_args()
    asyncio.run(main(args))
