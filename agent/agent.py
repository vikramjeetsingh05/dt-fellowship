#!/usr/bin/env python3
"""
Daily Reflection Tree Agent
Deterministic. No LLM at runtime. No randomness.
Usage: python agent.py [--tree path/to/reflection-tree.json]
"""

import json
import sys
import os
import textwrap
from datetime import datetime


# ─── Terminal colours (graceful fallback on Windows) ──────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    C_PROMPT   = Fore.CYAN + Style.BRIGHT
    C_OPTION   = Fore.WHITE
    C_REFLECT  = Fore.YELLOW
    C_BRIDGE   = Fore.GREEN
    C_SUMMARY  = Fore.MAGENTA + Style.BRIGHT
    C_DIM      = Style.DIM
    C_RESET    = Style.RESET_ALL
except ImportError:
    C_PROMPT = C_OPTION = C_REFLECT = C_BRIDGE = C_SUMMARY = C_DIM = C_RESET = ""


WIDTH = 72  # wrap width


# ─── Helpers ──────────────────────────────────────────────────────────────────

def wrap(text, indent=0):
    prefix = " " * indent
    return textwrap.fill(text, width=WIDTH, initial_indent=prefix, subsequent_indent=prefix)


def hr(char="─"):
    print(C_DIM + char * WIDTH + C_RESET)


def pause(prompt="  Press Enter to continue…"):
    try:
        input(C_DIM + prompt + C_RESET)
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)


def interpolate(text, state):
    """Replace {node_id.answer} and {axis1.summary} etc. placeholders."""
    if not text:
        return text
    for key, val in state["answers"].items():
        text = text.replace("{" + key + ".answer}", str(val))
    for ax in ["axis1", "axis2", "axis3"]:
        dominant = compute_dominant(state, ax)
        summary = state["summary_texts"].get(ax, "")
        text = text.replace("{" + ax + ".dominant}", dominant)
        text = text.replace("{" + ax + ".summary}", summary)
    text = text.replace("{closing_reflection}", state.get("closing_reflection", ""))
    return text


def compute_dominant(state, axis):
    counts = state["signals"].get(axis, {})
    if not counts:
        return "mixed"
    return max(counts, key=counts.get)


# ─── Tree loader ──────────────────────────────────────────────────────────────

def load_tree(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    nodes = {n["id"]: n for n in data["nodes"]}
    templates = data.get("summary_templates", {})
    return nodes, templates


# ─── Decision routing ─────────────────────────────────────────────────────────

def resolve_decision(node, state, nodes):
    """
    Parse decision node options like:
      "answer=Productive|Mixed:A1_Q_AGENCY_HIGH"
    or signal-based:
      "signal=axis1.dominant=internal:A1_R_INT"
    Returns next node id.
    """
    rules = node["options"]
    last_answer = state.get("last_answer", "")

    for rule in rules:
        if ":" not in rule:
            continue
        condition, target = rule.split(":", 1)
        condition = condition.strip()
        target = target.strip()

        if condition.startswith("answer="):
            values = condition[len("answer="):].split("|")
            if last_answer in values:
                return target

        elif condition.startswith("signal="):
            # e.g. signal=axis1.dominant=internal
            parts = condition[len("signal="):].split("=")
            if len(parts) == 2:
                axis_key, expected = parts
                ax, metric = axis_key.split(".")
                actual = compute_dominant(state, ax)
                if actual == expected:
                    return target

    # fallback: first rule's target
    if rules:
        return rules[0].split(":")[-1].strip()
    return None


# ─── Signal accumulation ──────────────────────────────────────────────────────

def record_signal(signal, state):
    if not signal:
        return
    parts = signal.split(":")
    if len(parts) != 2:
        return
    axis, pole = parts
    if axis not in state["signals"]:
        state["signals"][axis] = {}
    state["signals"][axis][pole] = state["signals"][axis].get(pole, 0) + 1


# ─── Summary building ─────────────────────────────────────────────────────────

def build_summary_texts(state, templates):
    axis_map = {
        "axis1": {"internal": "internal", "external": "external", "mixed": "mixed"},
        "axis2": {"contribution": "contribution", "entitlement": "entitlement", "mixed": "mixed"},
        "axis3": {"altrocentric": "altrocentric", "collective": "collective", "self": "self"},
    }
    positives = 0
    for ax, pole_map in axis_map.items():
        dominant = compute_dominant(state, ax)
        pole_key = pole_map.get(dominant, "mixed")
        text = templates.get(ax, {}).get(pole_key, "")
        state["summary_texts"][ax] = text
        if pole_key in ("internal", "contribution", "altrocentric", "collective"):
            positives += 1

    closing_templates = templates.get("closing", {})
    if positives == 3:
        state["closing_reflection"] = closing_templates.get("all_positive", "")
    elif positives == 0:
        state["closing_reflection"] = closing_templates.get("all_negative", "")
    else:
        state["closing_reflection"] = closing_templates.get("mixed", "")


# ─── Node renderers ───────────────────────────────────────────────────────────

def render_start(node, state):
    print()
    hr("═")
    print()
    print(C_BRIDGE + wrap(node["text"]) + C_RESET)
    print()
    pause()


def render_question(node, state):
    print()
    hr()
    print()
    text = interpolate(node["text"], state)
    print(C_PROMPT + wrap(text) + C_RESET)
    print()
    options = node["options"]
    for i, opt in enumerate(options, 1):
        print(C_OPTION + f"  {i}. {opt}" + C_RESET)
    print()

    while True:
        try:
            raw = input(C_DIM + "  Your choice (enter number): " + C_RESET).strip()
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                chosen = options[idx]
                state["answers"][node["id"]] = chosen
                state["last_answer"] = chosen
                record_signal(node.get("signal"), state)
                print(C_DIM + f"\n  ✓ '{chosen}'\n" + C_RESET)
                return
            else:
                print(f"  Please enter a number between 1 and {len(options)}.")
        except (ValueError, EOFError):
            print(f"  Please enter a number between 1 and {len(options)}.")
        except KeyboardInterrupt:
            sys.exit(0)


def render_reflection(node, state):
    print()
    hr()
    print()
    text = interpolate(node["text"], state)
    record_signal(node.get("signal"), state)
    # Indent reflection text for visual distinction
    for line in textwrap.wrap(text, width=WIDTH - 4):
        print(C_REFLECT + "    " + line + C_RESET)
    print()
    pause()


def render_bridge(node, state):
    print()
    text = interpolate(node["text"], state)
    print(C_BRIDGE + "  ── " + text + C_RESET)
    print()
    pause("  Press Enter to continue…")


def render_summary(node, state, templates):
    build_summary_texts(state, templates)
    print()
    hr("═")
    print()
    print(C_SUMMARY + "  YOUR REFLECTION SUMMARY" + C_RESET)
    print()
    text = interpolate(node["text"], state)
    for para in text.split("\n"):
        para = para.strip()
        if para:
            print(C_SUMMARY + wrap(para, indent=2) + C_RESET)
            print()
    pause()


def render_end(node, state):
    print()
    hr("═")
    print()
    print(C_DIM + wrap(node["text"], indent=2) + C_RESET)
    print()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(C_DIM + f"  Session ended: {now}" + C_RESET)
    print()


# ─── Walker ───────────────────────────────────────────────────────────────────

def get_next_node_id(node, state, nodes):
    """
    Priority order:
    1. 'target' field (explicit jump)
    2. decision node routing
    3. first child in nodes dict (parentId match)
    """
    if node.get("target"):
        return node["target"]

    if node["type"] == "decision":
        return resolve_decision(node, state, nodes)

    # find first child
    for n in nodes.values():
        if n.get("parentId") == node["id"]:
            return n["id"]

    return None


def walk(nodes, templates):
    state = {
        "answers": {},
        "signals": {},
        "last_answer": "",
        "summary_texts": {},
        "closing_reflection": "",
    }

    current_id = "START"
    visited = set()

    while current_id:
        if current_id in visited and nodes[current_id]["type"] not in ("decision",):
            # safety: avoid infinite loops on non-decision nodes
            break
        visited.add(current_id)

        node = nodes.get(current_id)
        if not node:
            print(f"[ERROR] Node '{current_id}' not found in tree.")
            break

        ntype = node["type"]

        if ntype == "start":
            render_start(node, state)
        elif ntype == "question":
            render_question(node, state)
        elif ntype == "decision":
            pass  # invisible to user
        elif ntype == "reflection":
            render_reflection(node, state)
        elif ntype == "bridge":
            render_bridge(node, state)
        elif ntype == "summary":
            render_summary(node, state, templates)
        elif ntype == "end":
            render_end(node, state)
            break

        current_id = get_next_node_id(node, state, nodes)


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    tree_path = "tree/reflection-tree.json"
    if len(sys.argv) > 2 and sys.argv[1] == "--tree":
        tree_path = sys.argv[2]
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        tree_path = sys.argv[1]

    if not os.path.exists(tree_path):
        # try relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tree_path = os.path.join(script_dir, "..", "tree", "reflection-tree.json")

    if not os.path.exists(tree_path):
        print(f"[ERROR] Tree file not found: {tree_path}")
        print("Usage: python agent.py --tree path/to/reflection-tree.json")
        sys.exit(1)

    nodes, templates = load_tree(tree_path)
    walk(nodes, templates)


if __name__ == "__main__":
    main()
