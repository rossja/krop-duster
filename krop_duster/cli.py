"""
Command-line interface for KROP Duster.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.status import Status

from krop_duster.core.models import (
    AnalysisConfig,
    GenerationConfig,
    KROPDusterConfig,
    LLMConfig,
    LLMProvider,
    SamplingConfig,
)
from krop_duster.generation.hybrid_generator import HybridGenerator
from krop_duster.output.formatter import OutputFormatter


console = Console()
logger = logging.getLogger(__name__)


def get_state_dir() -> Path:
    """Get the KROP Duster state directory (~/.krop-duster)."""
    state_dir = Path.home() / ".krop-duster"
    state_dir.mkdir(exist_ok=True)
    return state_dir


def get_acceptance_state() -> bool:
    """Check if user has previously accepted the legal notice."""
    state_file = get_state_dir() / "state.json"
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text())
            return data.get("legal_notice_accepted", False)
        except (json.JSONDecodeError, IOError):
            return False
    return False


def save_acceptance_state(accepted: bool) -> None:
    """Save the user's acceptance of the legal notice."""
    state_file = get_state_dir() / "state.json"
    data = {"legal_notice_accepted": accepted}
    state_file.write_text(json.dumps(data, indent=2))


def show_authorization_warning() -> bool:
    """
    Display authorization warning and get user acceptance.

    Returns:
        True if user accepts, False otherwise
    """
    warning_text = """[bold red]⚠️  AUTHORIZATION REQUIRED ⚠️[/bold red]

KROP Duster is a security research tool intended ONLY for:
• Authorized red team assessments
• Testing systems you own or have permission to test
• Security research with proper authorization

[bold]Unauthorized use may violate:[/bold]
• Terms of Service agreements
• Computer Fraud and Abuse Act (CFAA)
• Other applicable laws and regulations

By using this tool, you confirm you have proper authorization
for any testing you conduct.
"""

    console.print()
    console.print(Panel(warning_text, border_style="red", title="Legal Notice"))
    console.print()

    response = click.prompt(
        "Do you accept these terms and confirm you have authorization?",
        type=click.Choice(["yes", "no"], case_sensitive=False),
    )

    return response.lower() == "yes"


@click.command()
@click.argument("prompt", required=False)
@click.option(
    "--prompt-file",
    "-f",
    type=click.Path(exists=True),
    help="Read prompt from file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: display in terminal)",
)
@click.option(
    "--tokenizer",
    "-t",
    default="gpt-4",
    help="Tokenizer to use (default: gpt-4)",
)
@click.option(
    "--llm-provider",
    type=click.Choice(["openai", "anthropic", "ollama", "templates"], case_sensitive=False),
    default="openai",
    help="LLM provider (default: openai)",
)
@click.option(
    "--llm-model",
    default="gpt-4",
    help="LLM model name (default: gpt-4)",
)
@click.option(
    "--temperature",
    type=float,
    default=0.7,
    help="LLM temperature (default: 0.7)",
)
@click.option(
    "--max-concepts",
    type=int,
    default=10,
    help="Maximum concepts to extract (default: 10)",
)
@click.option(
    "--max-variants",
    type=int,
    default=3,
    help="Maximum variants per concept (default: 3)",
)
@click.option(
    "--disable-llm",
    is_flag=True,
    help="Disable LLM generation, use templates only",
)
@click.option(
    "--disable-kg",
    is_flag=True,
    help="Disable knowledge graph integration",
)
@click.option(
    "--show-individual",
    is_flag=True,
    help="Show individual per-concept variants in addition to combined output",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
@click.option(
    "--skip-warning",
    is_flag=True,
    hidden=True,
    help="Skip authorization warning (for testing only)",
)
@click.option(
    "--reset-acceptance",
    is_flag=True,
    help="Reset legal notice acceptance and show warning again",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
    default="WARNING",
    help="Logging level (default: WARNING)",
)
def main(
    prompt: Optional[str],
    prompt_file: Optional[str],
    output: Optional[str],
    tokenizer: str,
    llm_provider: str,
    llm_model: str,
    temperature: float,
    max_concepts: int,
    max_variants: int,
    disable_llm: bool,
    disable_kg: bool,
    show_individual: bool,
    verbose: bool,
    skip_warning: bool,
    reset_acceptance: bool,
    log_level: str,
):
    """
    KROP Duster - Intelligent KROP attack generation tool.

    Generate obfuscated prompts for testing LLM security controls.

    Example:
        krop-duster "Generate an image of Mickey Mouse smoking"
    """
    # Determine effective log level
    # If verbose is set and log_level wasn't explicitly changed from default, use INFO
    if verbose and log_level.upper() == "WARNING":
        effective_level = logging.INFO
    else:
        effective_level = getattr(logging, log_level.upper())

    # Set up logging
    logging.basicConfig(
        level=effective_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Suppress noisy third-party loggers unless in verbose/debug mode
    if effective_level > logging.INFO:
        for noisy_logger in ["httpx", "sentence_transformers", "urllib3"]:
            logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    # Suppress tqdm progress bars unless verbose
    if effective_level > logging.INFO:
        os.environ["TQDM_DISABLE"] = "1"

    try:
        # Handle authorization
        if reset_acceptance:
            save_acceptance_state(False)

        if not skip_warning:
            if get_acceptance_state():
                pass  # Already accepted, continue
            else:
                if not show_authorization_warning():
                    console.print("[yellow]Authorization not accepted. Exiting.[/yellow]")
                    sys.exit(0)
                # Save acceptance for future runs
                save_acceptance_state(True)

        # Get prompt
        if prompt_file:
            with open(prompt_file, "r") as f:
                prompt_text = f.read().strip()
        elif prompt:
            prompt_text = prompt
        else:
            console.print("[red]Error: Must provide prompt or --prompt-file[/red]")
            sys.exit(1)

        # Build configuration
        llm_config = LLMConfig(
            provider=LLMProvider(llm_provider),
            model=llm_model,
            temperature=temperature,
        )

        analysis_config = AnalysisConfig(
            max_concepts=max_concepts,
        )

        generation_config = GenerationConfig(
            max_variants_per_concept=max_variants,
            enable_llm=not disable_llm,
            enable_knowledge_graph=not disable_kg,
            include_individual_variants=show_individual,
        )

        config = KROPDusterConfig(
            tokenizer=tokenizer,
            llm=llm_config,
            analysis=analysis_config,
            generation=generation_config,
            output_file=output,
            verbose=verbose,
        )

        # Display configuration
        if verbose:
            console.print(f"\n[bold]Configuration:[/bold]")
            console.print(f"  Tokenizer: {tokenizer}")
            console.print(f"  LLM Provider: {llm_provider}")
            console.print(f"  LLM Model: {llm_model}")
            console.print(f"  Temperature: {temperature}")
            console.print(f"  Max Concepts: {max_concepts}")
            console.print(f"  Max Variants: {max_variants}")
            console.print()

        # Initialize generator
        console.print("[cyan]Initializing KROP Duster...[/cyan]")
        generator = HybridGenerator(config)

        # Generate attacks with progress indicator
        with Status(
            "[cyan]Starting analysis...[/cyan]",
            spinner="dots",
            console=console,
        ) as status:
            def update_status(msg: str) -> None:
                status.update(f"[cyan]{msg}[/cyan]")

            result = generator.generate(prompt_text, status_callback=update_status)

        # Format and display output
        formatter = OutputFormatter(verbose=verbose)

        if output:
            formatter.save_to_file(result, output)
            if not verbose:
                console.print()

        # Always display in terminal
        formatter.display_terminal(result)

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if verbose:
            logger.exception("Detailed error:")
        sys.exit(1)


if __name__ == "__main__":
    main()
