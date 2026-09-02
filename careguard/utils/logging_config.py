"""Apply config/logging.yaml, falling back to basicConfig."""
from __future__ import annotations

import logging
import logging.config
from pathlib import Path

_CONFIGURED = False


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True
    path = Path(__file__).resolve().parents[2] / "config" / "logging.yaml"
    try:
        import yaml

        logging.config.dictConfig(yaml.safe_load(path.read_text(encoding="utf-8")))
    except Exception:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
