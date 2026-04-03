import argparse
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
from services.PromptBuilder import PromptBuilder


async def main(args: Namespace) -> None:

    # ── Build system prompt dynamically ──────────────────────────────────────
    builder = PromptBuilder(mode=args.prompt_mode, max_chars=args.max_prompt_chars)

    # Load identity from config file
    if args.identity:
        try:
            builder.add_identity(args.identity)
            print(f"  [Identity loaded from {args.identity}]")
        except Exception as e:
            print(f"  [Identity load failed: {e}]")
            return

    # Always inject current date/time
    builder.add_datetime()

    # Load workspace bootstrap rules if requested
    if args.bootstrap:
        builder.add_bootstrap(args.bootstrap)
        print(f"  [Bootstrap loaded from {args.bootstrap}]")

    # ── Build the system prompt ───────────────────────────────────────────────
    from tools.tools import registry

    # Filter tools if --tools is specified
    if args.tools:
        requested = set(args.tools)
        available = set(registry.tool_spec.keys())
        unknown = requested - available
        if unknown:
            print(f"  [Warning: unknown tools: {', '.join(unknown)}. Available: {', '.join(available)}]")
        registry.tool_spec = {k: v for k, v in registry.tool_spec.items() if k in requested}
        registry.tool_function = {k: v for k, v in registry.tool_function.items() if k in requested}
        print(f"  [Tools enabled: {', '.join(registry.tool_spec.keys())}]")

    builder.add_tools(registry)
    system_prompt = builder.build()

    if args.verbose:
        print(f"\n{'─'*60}")
        print("SYSTEM PROMPT PREVIEW:")
        print(system_prompt[:500] + ("..." if len(system_prompt) > 500 else ""))
        print(f"{'─'*60}\n")

    # ── Initialize LLM client ─────────────────────────────────────────────────
    try:
        client: AsyncBaseLLMClient = ProviderFactory.from_model(
            model_name=args.model,
            instructions=system_prompt,
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
                # Search for relevant chunks
                rag_results = await chunk_ctx.search(query, top_k=10)

                if rag_results:
                    print(f"  [Context attached from {len(rag_results)} chunk(s)]")

                    # Inject structured RAG results into PromptBuilder memory section
                    # and rebuild system prompt dynamically for this query
                    builder.sections.pop("memory", None)
                    builder.add_memory(rag_results)
                    updated_prompt = builder.build()
                    client.instructions = updated_prompt

                    # Also enrich the user query with context (for user message)
                    context = chunk_ctx.format_context(rag_results)
                    if context:
                        enriched_query = f"{context}\n\n{query}"

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

    # ── LLM settings ──────────────────────────────────────────────────────────
    parser.add_argument("--stream", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--model", default="gpt-5.2")

    # ── PromptBuilder settings ────────────────────────────────────────────────
    parser.add_argument("--identity", required=True,
                        help="Path to identity config file (YAML or JSON) e.g. restaurants/my-delhi/config.json")
    parser.add_argument("--prompt-mode", default="full", choices=["full", "minimal", "none"],
                        help="Prompt assembly mode: full (all sections), minimal (identity+datetime+tools), none (empty)")
    parser.add_argument("--tools", nargs="*", default=None,
                        help="Whitelist of tools to enable e.g. --tools get_place_details read_file (default: all tools)")
    parser.add_argument("--max-prompt-chars", type=int, default=32000,
                        help="Maximum characters in the assembled system prompt (default: 32000)")
    parser.add_argument("--bootstrap", default=None,
                        help="Directory to scan for AGENTS.md workspace rules (e.g. '.')")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction, default=False,
                        help="Show system prompt preview on startup")

    # ── RAG / Chunk settings ──────────────────────────────────────────────────
    parser.add_argument("--chunks", action=argparse.BooleanOptionalAction, default=False,
                        help="Enable chunk context (RAG) from the local chunk database")
    parser.add_argument("--chunk-db", default="data/pageindex_cache.db",
                        help="Path to the chunk SQLite database")
    parser.add_argument("--ranker-model", default="gpt-4.1-mini",
                        help="LLM model used to rank chunk relevance (default: gpt-4.1-mini)")

    args: Namespace = parser.parse_args()
    asyncio.run(main(args))
