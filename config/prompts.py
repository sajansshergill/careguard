"""Loads prompt templates from config/prompts/*.md.

Keeps prompt text out of code so it can be versioned and diffed on its own.
Agents call load_prompt("reasoner") instead of hardcoding SYSTEM strings.
"""
from functools import cache
from pathlib import Path

_PROMPT_DIR = Path(__file__).parent / "prompts"


@cache
def load_prompt(name: str) -> str:
    path = _PROMPT_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()
