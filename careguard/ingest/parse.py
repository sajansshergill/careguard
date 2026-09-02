"""Read raw policy documents into a flat list of {policy_id, text}."""
from __future__ import annotations

import glob
import os


def load_policies(source_dir: str) -> list[dict]:
    docs = []
    for path in sorted(glob.glob(os.path.join(source_dir, "*"))):
        policy_id = os.path.splitext(os.path.basename(path))[0]
        ext = os.path.splitext(path)[1].lower()
        if ext == ".txt":
            with open(path, encoding="utf-8") as f:
                docs.append({"policy_id": policy_id, "text": f.read()})
        elif ext == ".pdf":
            text = _read_pdf(path)
            if text:
                docs.append({"policy_id": policy_id, "text": text})
    return docs


def _read_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)
