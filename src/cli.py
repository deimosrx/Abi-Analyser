# cli.py
import os, json, datetime
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from abi_parser import (
    load_abi, get_by_type, print_summary,
    print_functions_table, print_events_table,
    print_errors_table, print_constructor_info, print_fallbacks
)
from function_analyzer import analyze_functions

console = Console()
loaded_abi = None
loaded_path = None

def cmd_help():
    table = Table(title="Available Commands", show_lines=True)
    table.add_column("Command", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_row("load <path>", "Load ABI JSON file (or use 'info <path>')")
    table.add_row("info [path]", "Load and print full ABI summary/tables (stores ABI in session)")
    table.add_row("analyze", "Run security heuristics & complexity analysis on loaded ABI")
    table.add_row("function <name>", "Show raw JSON for a specific function")
    table.add_row("search <keyword>", "Search ABI entries by keyword")
    table.add_row("selectors", "List function signatures and 4-byte selectors")
    table.add_row("export [out.md]", "Export full Markdown report (defaults to reports/abi_report.md)")
    table.add_row("detect-erc", "Attempt to detect token standard (ERC20/ERC721/ERC1155)")
    table.add_row("help", "Show this help")
    table.add_row("exit", "Exit the program")
    console.print(table)

def cmd_load(path):
    global loaded_abi, loaded_path
    path = os.path.expanduser(os.path.expandvars(path))
    abi = load_abi(path)
    if abi is not None:
        loaded_abi = abi
        loaded_path = path

def cmd_info(path=None):
    global loaded_abi, loaded_path
    if path:
        cmd_load(path)
    if not loaded_abi:
        console.print("[red]No ABI loaded. Use: load <path> or info <path>[/red]")
        return
    functions = get_by_type(loaded_abi, "function")
    events = get_by_type(loaded_abi, "event")
    errors = get_by_type(loaded_abi, "error")
    constructors = get_by_type(loaded_abi, "constructor")
    fallbacks = [it for it in loaded_abi if it.get("type") in ("fallback","receive")]

    print_summary(functions, events, errors, constructors, fallbacks)
    print_functions_table(functions)
    print_events_table(events)
    print_errors_table(errors)
    print_constructor_info(constructors)
    print_fallbacks(fallbacks)
    console.rule("[green]End of Report")

def cmd_analyze():
    if not loaded_abi:
        console.print("[red]No ABI loaded. Use 'info <path>' or 'load <path>' first.[/red]")
        return
    console.rule("[yellow]Function Risk & Complexity Analysis")
    result = analyze_functions(loaded_abi)
    funcs = result["functions"]

    table = Table(title="Risk & Complexity", show_lines=True)
    table.add_column("#", style="cyan")
    table.add_column("Function", style="green")
    table.add_column("Selector", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Inputs", style="white")
    table.add_column("Complexity", style="red")
    table.add_column("Risk", style="bold red")

    for i, f in enumerate(funcs, 1):
        table.add_row(str(i), f["name"], f["selector"], f["state"], ", ".join(f["inputs"]) or "—", f["complexity"], f["risk"])
    console.print(table)

    # print summary info
    s = result["summary"]
    if s["overloaded_names"]:
        console.print(f"[yellow]Overloaded function names:[/yellow] {s['overloaded_names']}")
    if s["selector_collisions"]:
        console.print(f"[red]Selector collisions detected:[/red]")
        for sel, sigs in s["selector_collisions"].items():
            console.print(f" {sel} -> {sigs}")
    console.rule("[yellow]End Analysis")

def cmd_function(name):
    if not loaded_abi:
        console.print("[red]No ABI loaded.[/red]")
        return
    functions = get_by_type(loaded_abi, "function")
    matches = [f for f in functions if f.get("name","").lower() == name.lower()]
    if not matches:
        console.print(f"[red]Function '{name}' not found.[/red]")
        return
    # pretty print JSON for function
    console.print_json(data=matches[0])

def cmd_search(keyword):
    if not loaded_abi:
        console.print("[red]No ABI loaded.[/red]")
        return
    kw = keyword.lower()
    found = [it for it in loaded_abi if kw in json.dumps(it).lower()]
    if not found:
        console.print(f"[yellow]No matches for '{keyword}'.[/yellow]")
        return
    table = Table(title=f"Search results for '{keyword}'", show_lines=False)
    table.add_column("#", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Name / snippet", style="white")
    for i, it in enumerate(found, 1):
        t = it.get("type","?")
        name = it.get("name") or json.dumps(it)[:80]
        table.add_row(str(i), t, name)
    console.print(table)

def cmd_selectors():
    if not loaded_abi:
        console.print("[red]No ABI loaded.[/red]")
        return
    functions = get_by_type(loaded_abi, "function")
    table = Table(title="Signatures & Selectors", show_lines=True)
    table.add_column("#", style="cyan")
    table.add_column("Signature", style="magenta")
    table.add_column("Selector (4-byte)", style="yellow")
    for i, f in enumerate(functions, 1):
        sig = f"{f.get('name','')}(" + ",".join([inp.get("type","") for inp in f.get("inputs",[])]) + ")"
        sel = analyze_functions.__module__  # placeholder to avoid unused import; we'll compute below
        # compute selector using function_analyzer selector routine via analyze_functions return
        # shortcut: call analyze_functions and map
    # compute map:
    analysis = analyze_functions(loaded_abi)
    for i, f in enumerate(analysis["functions"], 1):
        table.add_row(str(i), f["signature"], f["selector"])
    console.print(table)

def cmd_detect_erc():
    if not loaded_abi:
        console.print("[red]No ABI loaded.[/red]")
        return
    functions = [f.get("name","") for f in get_by_type(loaded_abi, "function")]
    token_type = "Unknown"
    if all(x in functions for x in ["name","symbol","decimals","totalSupply","transfer","approve","allowance"]):
        token_type = "ERC20"
    elif any(x in functions for x in ["ownerOf","safeTransferFrom"]) and "balanceOf" in functions:
        token_type = "ERC721"
    elif "uri" in functions and "safeTransferFrom" in functions:
        token_type = "ERC1155"
    console.print(f"[blue]Detected token type:[/blue] [green]{token_type}[/green]")

def cmd_export(out_path=None):
    if not loaded_abi:
        console.print("[red]No ABI loaded.[/red]")
        return
    out_dir = "reports"
    os.makedirs(out_dir, exist_ok=True)
    if not out_path:
        filename = f"abi_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        out_path = os.path.join(out_dir, filename)
    else:
        out_path = os.path.join(out_dir, out_path) if not os.path.isabs(out_path) else out_path

    analysis = analyze_functions(loaded_abi)
    functions = analysis["functions"]
    summary = analysis["summary"]
    events = get_by_type(loaded_abi, "event")
    errors = get_by_type(loaded_abi, "error")
    constructors = get_by_type(loaded_abi, "constructor")
    fallbacks = [it for it in loaded_abi if it.get("type") in ("fallback","receive")]

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# ABI Analysis Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Functions: {len(functions)}\n")
        f.write(f"- Events: {len(events)}\n")
        f.write(f"- Errors: {len(errors)}\n")
        f.write(f"- Constructors: {len(constructors)}\n")
        f.write(f"- Fallbacks/Receive: {len(fallbacks)}\n\n")

        f.write("## Token detection\n\n")
        funcs_names = [f["name"] for f in functions]
        token_type = "Unknown"
        if all(x in funcs_names for x in ["name","symbol","decimals","totalSupply"]):
            token_type = "Likely ERC20"
        f.write(f"- Type: {token_type}\n\n")

        f.write("## Functions (detailed)\n\n")
        for fn in functions:
            f.write(f"### {fn['name']}\n")
            f.write(f"- Signature: `{fn['signature']}`\n")
            f.write(f"- Selector: `{fn['selector']}`\n")
            f.write(f"- State: {fn['state']}\n")
            f.write(f"- Inputs: {', '.join(fn['inputs']) or '—'}\n")
            f.write(f"- Complexity: {fn['complexity']}\n")
            f.write(f"- Risk: {fn['risk']}\n")
            f.write(f"- Notes: {fn['desc']}\n\n")

        f.write("## Analysis summary\n\n")
        f.write(f"- Overloaded names: {summary.get('overloaded_names')}\n")
        f.write(f"- Selector collisions: {summary.get('selector_collisions')}\n\n")

        f.write("## Recommendations\n\n")
        f.write("- Review high/critical functions in source/bytecode.\n")
        f.write("- Check access control for sensitive functions (mint, upgrade, withdraw).\n")
        f.write("- Review payable & fallback functions for safety and reentrancy.\n")
        f.write("- If possible, run static analysis tools (Slither / Mythril) on the source/bytecode.\n")

    console.print(f"[green]Report saved to:[/green] {out_path}")

# Main loop
def main_loop():
    console.print("[bold green]Welcome to ABI Analyzer (interactive)[/bold green]")
    console.print("Type 'help' to list commands.\n")
    while True:
        try:
            line = Prompt.ask("[cyan]abi-analyzer >[/cyan]").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd == "help":
                cmd_help()
            elif cmd == "load":
                if not args:
                    console.print("[red]Usage: load <path>[/red]")
                else:
                    cmd_load(args[0])
            elif cmd == "info":
                cmd_info(args[0] if args else None)
            elif cmd == "analyze":
                cmd_analyze()
            elif cmd == "function":
                if not args:
                    console.print("[red]Usage: function <name>[/red]")
                else:
                    cmd_function(args[0])
            elif cmd == "search":
                cmd_search(" ".join(args)) if args else console.print("[red]Usage: search <keyword>[/red]")
            elif cmd == "selectors":
                cmd_selectors()
            elif cmd == "detect-erc":
                cmd_detect_erc()
            elif cmd == "export":
                cmd_export(args[0] if args else None)
            elif cmd in ("exit","quit"):
                console.print("[red]Exiting...[/red]")
                break
            else:
                console.print(f"[red]Unknown command:[/red] {cmd}  (type 'help')")
        except KeyboardInterrupt:
            console.print("\n[red]Interrupted. Type 'exit' to quit.[/red]")
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")

if __name__ == "__main__":
    main_loop()
