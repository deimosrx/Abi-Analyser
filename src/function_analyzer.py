# function_analyzer.py
from rich.console import Console
from eth_utils import keccak, to_hex
console = Console()

SENSITIVE_KEYWORDS = [
    "mint", "burn", "upgrade", "setowner", "transferownership", "renounce",
    "pause", "unpause", "blacklist", "withdraw", "claim", "setfee", "admin",
    "initialize", "owner", "approve"
]

def function_signature(func):
    name = func.get("name","")
    types = ",".join([inp.get("type","") for inp in func.get("inputs", [])])
    return f"{name}({types})"

def selector_of(signature):
    try:
        h = keccak(text=signature)
        return to_hex(h[:4])
    except Exception:
        return "n/a"

def compute_complexity(func):
    inputs = func.get("inputs", []) or []
    dynamic = any(t.get("type","").endswith("[]") or t.get("type","") in ("string","bytes") for t in inputs)
    count = len(inputs)
    score = count + (2 if dynamic else 0)
    if score >= 5:
        return "High"
    if score >= 3:
        return "Medium"
    return "Low"

def classify_risk(func, abi):
    name = func.get("name","").lower()
    state = func.get("stateMutability","")
    inputs = func.get("inputs", []) or []

    # heuristics
    risk = "Low"
    reasons = []

    # sensitive names
    for kw in SENSITIVE_KEYWORDS:
        if kw in name:
            risk = "High"
            reasons.append(f"Sensitive name match: '{kw}'")

    # payable
    if state == "payable":
        reasons.append("Payable function (receives ETH)")
        if risk != "High":
            risk = "Medium"

    # many inputs or dynamic types
    complexity = compute_complexity(func)
    if complexity == "High":
        reasons.append("High complexity (many or dynamic inputs)")
        if risk == "Low":
            risk = "Medium"

    # view/pure reduce risk
    if state in ("view","pure") and risk == "Low":
        reasons.append("Read-only function")

    # selector collisions (cheap check - compute signature and compare later at analyze stage)
    sig = function_signature(func)

    desc = "; ".join(reasons) if reasons else "No immediate indicators"
    return {
        "name": func.get("name",""),
        "signature": sig,
        "selector": selector_of(sig),
        "state": state,
        "inputs": [inp.get("type","") for inp in inputs],
        "complexity": complexity,
        "risk": risk,
        "desc": desc
    }

def analyze_functions(abi):
    """Return list of analysis dicts for each function and global warnings."""
    functions = [f for f in abi if f.get("type") == "function"]
    results = [classify_risk(f, abi) for f in functions]

    # detect overloaded names
    name_counts = {}
    for r in results:
        name_counts[r["name"]] = name_counts.get(r["name"], 0) + 1
    overloads = [n for n,c in name_counts.items() if c>1]

    # detect selector collisions
    sel_map = {}
    for r in results:
        sel_map.setdefault(r["selector"], []).append(r["signature"])
    collisions = {sel:sigs for sel,sigs in sel_map.items() if len(set(sigs))>1 and sel != "n/a"}

    summary = {
        "total_functions": len(results),
        "overloaded_names": overloads,
        "selector_collisions": collisions
    }

    return {
        "functions": results,
        "summary": summary
    }
