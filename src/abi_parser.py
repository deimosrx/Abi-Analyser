# abi_parser.py
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns

console = Console()

def load_abi(path):
    """Load ABI JSON file and return the ABI list or None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            abi = json.load(f)
        console.print(f"[green]Loaded ABI:[/green] {path} ({len(abi)} items)")
        return abi
    except FileNotFoundError:
        console.print(f"[red]File not found:[/red] {path}")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[red]Invalid JSON:[/red] {e}")
        return None

def get_by_type(abi, item_type):
    """Return ABI items of a specific type (function, event, constructor, error...)."""
    if not abi:
        return []
    return [item for item in abi if item.get("type") == item_type]

def print_summary(functions, events, errors, constructors, fallbacks):
    stats = {
        "Functions": len(functions),
        "Events": len(events),
        "Errors": len(errors),
        "Constructors": len(constructors),
        "Fallbacks/Receive": len(fallbacks),
    }

    panels = []
    for key, value in stats.items():
        panels.append(
            Panel.fit(
                f"[white]{value}[/white]",
                title=f"[cyan]{key}[/cyan]",
                border_style="green",
            )
        )

    console.rule("[magenta]📊 ABI Summary Overview")
    console.print(Columns(panels))
    console.print("\n")

def print_functions_table(functions):
    table = Table(title="📋 Contract Functions", show_lines=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Function Name", style="bold green")
    table.add_column("Inputs", style="magenta")
    table.add_column("Outputs", style="blue")
    table.add_column("State Mutability", style="yellow")

    for i, func in enumerate(functions, 1):
        name = func.get("name", "—")
        inputs = ", ".join([inp.get("type","?") for inp in func.get("inputs", [])]) or "—"
        outputs = ", ".join([out.get("type","?") for out in func.get("outputs", [])]) or "—"
        state = func.get("stateMutability", "—")
        table.add_row(str(i), name, inputs, outputs, state)

    console.print(table)
    console.print("\n")

def print_events_table(events):
    table = Table(title="🎉 Contract Events", show_lines=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Event Name", style="bold green")
    table.add_column("Inputs", style="magenta")
    table.add_column("Indexed", style="yellow")

    for i, ev in enumerate(events, 1):
        name = ev.get("name", "—")
        inputs = ", ".join([inp.get("type","?") for inp in ev.get("inputs", [])]) or "—"
        indexed = ", ".join([str(inp.get("indexed", False)) for inp in ev.get("inputs", [])]) or "—"
        table.add_row(str(i), name, inputs, indexed)

    console.print(table)
    console.print("\n")

def print_errors_table(errors):
    table = Table(title="⚠️ Contract Errors", show_lines=True, header_style="bold cyan")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Error Name", style="bold red")
    table.add_column("Inputs", style="magenta")
    for i, err in enumerate(errors, 1):
        name = err.get("name", "—")
        inputs = ", ".join([inp.get("type","?") for inp in err.get("inputs", [])]) or "—"
        table.add_row(str(i), name, inputs)
    console.print(table)
    console.print("\n")

def print_constructor_info(constructors):
    if not constructors:
        return
    cons = constructors[0]
    inputs = ", ".join([inp.get("type","?") for inp in cons.get("inputs", [])]) or "—"
    console.print(
        Panel.fit(
            f"🏗️ Constructor\nInputs: [cyan]{inputs}[/cyan]",
            title="Constructor Info",
            border_style="blue",
        )
    )
    console.print("\n")

def print_fallbacks(fallbacks):
    if not fallbacks:
        return
    for f in fallbacks:
        console.print(
            Panel.fit(
                f"🔁 Type: [bold]{f.get('type','?')}[/bold]\nState Mutability: [yellow]{f.get('stateMutability','—')}[/yellow]",
                title="Fallback / Receive",
                border_style="magenta",
            )
        )
        console.print("\n")
