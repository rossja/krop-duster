"""
Output formatting for generation results.
"""

import json
import logging
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from krop_duster.core.models import GenerationResult


logger = logging.getLogger(__name__)


class OutputFormatter:
    """Format generation results for display."""

    def __init__(self, verbose: bool = False):
        """
        Initialize output formatter.

        Args:
            verbose: Whether to show verbose output
        """
        self.verbose = verbose
        self.console = Console()

    def format_json(self, result: GenerationResult) -> str:
        """
        Format result as JSON.

        Args:
            result: Generation result

        Returns:
            JSON string
        """
        data = {
            "original_prompt": result.analysis.original_prompt,
            "generation_time": result.generation_time,
            "concepts_analyzed": [
                {
                    "text": concept.text,
                    "entity_type": concept.entity_type.value,
                    "priority_score": concept.priority_score,
                    "filter_likelihood": concept.filter_likelihood,
                    "violation_types": [vt.value for vt in concept.violation_types],
                }
                for concept in result.analysis.concepts
            ],
            "attack_prompts": [
                {
                    "attack_prompt": ap.attack_prompt,
                    "original_prompt": ap.original_prompt,
                    "concepts_obfuscated": ap.concepts_obfuscated,
                    "total_tokens": ap.total_tokens,
                    "probability_score": ap.probability_score,
                    "variants": [
                        {
                            "original_concept": v.original_concept,
                            "obfuscated_text": v.obfuscated_text,
                            "strategy": v.strategy.value,
                            "probability_score": v.probability_score,
                            "semantic_similarity": v.semantic_similarity,
                            "token_count": v.token_count,
                        }
                        for v in ap.variants_used
                    ],
                }
                for ap in result.attack_prompts
            ],
            "metadata": result.metadata,
        }

        return json.dumps(data, indent=2)

    def display_terminal(self, result: GenerationResult) -> None:
        """
        Display results in terminal with rich formatting.

        Args:
            result: Generation result
        """
        # Header
        self.console.print("\n")
        self.console.print(
            Panel.fit(
                "[bold cyan]KROP Duster - Attack Generation Results[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print()

        # Analysis summary
        self.console.print("[bold]Analysis Summary[/bold]")
        self.console.print(f"Original Prompt: [italic]{result.analysis.original_prompt}[/italic]")
        self.console.print(f"Concepts Identified: {len(result.analysis.concepts)}")
        self.console.print(f"Generation Time: {result.generation_time:.2f}s")
        self.console.print()

        # Concepts table
        if self.verbose and result.analysis.concepts:
            concepts_table = Table(title="Extracted Concepts", box=box.ROUNDED)
            concepts_table.add_column("Concept", style="cyan")
            concepts_table.add_column("Type", style="magenta")
            concepts_table.add_column("Priority", justify="right", style="green")
            concepts_table.add_column("Filter Risk", justify="right", style="yellow")

            for concept in result.analysis.concepts:
                concepts_table.add_row(
                    concept.text,
                    concept.entity_type.value,
                    f"{concept.priority_score:.2f}",
                    f"{concept.filter_likelihood:.2f}",
                )

            self.console.print(concepts_table)
            self.console.print()

        # Attack prompts
        self.console.print(f"[bold]Generated {len(result.attack_prompts)} Attack Variants[/bold]")
        self.console.print()

        for i, attack_prompt in enumerate(result.attack_prompts, 1):
            # Create panel for each attack
            self.console.print(f"[bold cyan]Attack #{i}[/bold cyan]")
            self.console.print(f"Probability Score: [green]{attack_prompt.probability_score:.2f}[/green]")
            self.console.print(f"Total Tokens: {attack_prompt.total_tokens}")
            self.console.print()

            self.console.print("[bold]Attack Prompt:[/bold]")
            self.console.print(
                Panel(
                    attack_prompt.attack_prompt,
                    border_style="green",
                    box=box.ROUNDED,
                )
            )
            self.console.print()

            # Show variants if verbose
            if self.verbose:
                for variant in attack_prompt.variants_used:
                    self.console.print(f"  [dim]Strategy: {variant.strategy.value}[/dim]")
                    self.console.print(f"  [dim]Original: {variant.original_concept}[/dim]")
                    self.console.print(f"  [dim]Obfuscated: {variant.obfuscated_text}[/dim]")
                    self.console.print(
                        f"  [dim]Similarity: {variant.semantic_similarity:.2f}, "
                        f"Tokens: {variant.token_count}[/dim]"
                    )
                    self.console.print()

        self.console.print()

    def save_to_file(self, result: GenerationResult, filepath: str) -> None:
        """
        Save results to file.

        Args:
            result: Generation result
            filepath: Output file path
        """
        json_output = self.format_json(result)

        with open(filepath, "w") as f:
            f.write(json_output)

        logger.info(f"Results saved to {filepath}")
        self.console.print(f"[green]✓[/green] Results saved to {filepath}")
