"""Shared LLM client. Supports OpenAI, Ollama, and a deterministic mock."""
from __future__ import annotations

import json
import re

from careguard.agents.heuristic import classify
from config.settings import settings


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider
        self._client = None
        if self.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "ollama":
            from openai import OpenAI

            self._client = OpenAI(
                base_url=settings.ollama_base_url,
                api_key="ollama",
            )

    def complete(self, system: str, user: str) -> str:
        if self.provider == "mock":
            return self._mock(system, user)
        if self._client is None:
            raise RuntimeError(
                f"Unknown LLM_PROVIDER={self.provider!r}. Use mock, openai, or ollama."
            )
        resp = self._client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0,
        )
        return resp.choices[0].message.content or ""

    def complete_json(self, system: str, user: str) -> dict:
        raw = self.complete(system + "\nReturn ONLY valid JSON, no prose.", user)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _mock(self, system: str, user: str) -> str:
        key = system.lower()
        if "reasoner" in key:
            return json.dumps(_mock_reasoner(user))
        if "guardrail" in key or "critic" in key:
            return json.dumps(_mock_guardrail(user))
        if "judge" in key:
            return json.dumps(
                {
                    "supported": True,
                    "score": 0.85,
                    "reason": "Cited clause IDs resolve to retrieved policy text.",
                }
            )
        return "{}"


def _mock_reasoner(user: str) -> dict:
    service = _field(user, "SERVICE REQUESTED")
    notes = _field(user, "CLINICAL NOTES")
    clauses = re.findall(r"\[([^\]]+)\]\s*(.+)", user)
    # drop the service/notes lines that aren't clause rows
    clauses = [(cid, text.strip()) for cid, text in clauses if cid.startswith("POL") or "-" in cid]
    return classify(service, notes, clauses)


def _mock_guardrail(user: str) -> dict:
    clause_part, _, claim_part = user.partition("CLAIMS:")
    valid_ids = set(re.findall(r"\[([^\]]+)\]", clause_part))
    cited = re.findall(r"cites\s+(\S+)\)", claim_part)
    grounded = [cid for cid in cited if cid in valid_ids]
    n = len(cited) or 1
    rate = len(grounded) / n
    confidence = 0.88 if rate >= 0.99 else 0.45
    return {"grounded_clause_ids": grounded, "confidence": confidence}


def _field(user: str, label: str) -> str:
    match = re.search(rf"{label}:\s*(.+)", user)
    return match.group(1).strip() if match else ""


llm = LLMClient()
