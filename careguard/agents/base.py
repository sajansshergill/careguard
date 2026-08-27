"""Shared LLM client. Supports OpenAI-compatible APIs and a deterministic mock."""
from __future__ import annotations
import json
from config.settings import settings


class LLMClient:
    def __init__(self) -> None:
        self.provider = settings.llm_provider
        if self.provider == "openai":
            from openai import OpenAI
            self._client = OpenAI(api_key=settings.openai_api_key)

    def complete(self, system: str, user: str) -> str:
        if self.provider == "mock":
            return self._mock(system, user)
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
        return json.loads(raw)

    # --- deterministic mock so tests + demo run with no API key ---
    def _mock(self, system: str, user: str) -> str:
        if "reasoner" in system.lower():
            return json.dumps({
                "draft_decision": "route-to-human",
                "claims": [
                    {"text": "Requested service is listed in the policy scope.",
                     "clause_id": "MOCK-1"},
                    {"text": "Documentation of prior conservative therapy is present.",
                     "clause_id": "MOCK-2"},
                ],
                "rationale": "Case appears to meet listed criteria but documentation "
                             "completeness is uncertain; recommend human review.",
            })
        if "guardrail" in system.lower():
            return json.dumps({"grounded_clause_ids": ["MOCK-1", "MOCK-2"],
                               "confidence": 0.62})
        return "{}"


llm = LLMClient()