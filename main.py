import argparse
import json
import sys
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

    chunk_ctx = None
    if args.chunks:
        try:
            from services.ChunkContext import ChunkContext
            chunk_ctx = ChunkContext(db_path=args.chunk_db, model=args.ranker_model)
            loaded = chunk_ctx.load_chunks()
            if loaded > 0:
                print(f"Chunk context enabled: {loaded} chunks loaded from {args.chunk_db}")
            else:
                print(f"No chunks found in {args.chunk_db} — running without context")
                chunk_ctx = None
        except Exception as e:
            print(f"Could not load chunk DB: {e} — running without context")
            chunk_ctx = None

    print(f"Chat started with model '{args.model}'. Type 'exit' to quit.\n")

    while True:
        try:
            sys.stdout.flush()
            query: str = await asyncio.get_running_loop().run_in_executor(None, lambda: input("> "))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            if chunk_ctx:
                chunk_ctx.close()
            return

        if query.strip().lower() == "exit":
            print("Goodbye!")
            if chunk_ctx:
                chunk_ctx.close()
            return

        if not query.strip():
            continue

        enriched_query = query
        if chunk_ctx:
            try:
                # Get enriched query with full chunk context
                enriched_query = await chunk_ctx.enrich(query, top_k=8)
                if enriched_query != query:
                    # Context was added
                    num_chunks = enriched_query.count("---")
                    print(f"  [Context attached from {num_chunks} chunk(s)]")
            except Exception as e:
                print(f"  [Context routing failed: {e}]")

        try:
            if args.stream:
                await client.generate_response_streaming(query=enriched_query)
                sys.stdout.flush()
            else:
                await client.generate_response(query=enriched_query)
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
    parser.add_argument("--stream", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--model", default="gpt-5.2")
    parser.add_argument("--system-prompt", default="you are a generic chat-bot with access to tools")
    parser.add_argument("--chunks", action=argparse.BooleanOptionalAction, default=False,
                        help="Enable chunk context (RAG) from the local chunk database")
    parser.add_argument("--chunk-db", default="data/pageindex_cache.db",
                        help="Path to the chunk SQLite database")
    parser.add_argument("--ranker-model", default="gpt-4.1-mini",
                        help="LLM model used to rank chunk relevance (default: gpt-4.1-mini)")
    args: Namespace = parser.parse_args()
    asyncio.run(main(args))
