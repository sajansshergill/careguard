# CareGuard — Multi-Agent Prior Authorization Assistant

> An agentic AI system that triages prior-authorization (PA) requests against payer medical policy, returns a **citation-grounded** recommendation (approve / deny / route-to-human), and refuses to decide when it isn't confident — with a full audit trail and automated hallucination monitoring built in.

**Author:** Sajan Shergill · [Portfolio](https://sajansshergill.github.io) · [LinkedIn](https://linkedin.com/in/sajanshergill) · [GitHub](https://github.com/sajansshergill)

> ⚠️ **No PHI. Ever.** This project runs entirely on **synthetic cases** and **publicly available coverage-policy documents**. It is a technical demonstration, not a clinical or coverage-decision tool.

---

## Why this project exists

Prior authorization is one of the most expensive and most complained-about workflows in health insurance. A clinician submits a request, someone has to check it against pages of medical-policy criteria, and the turnaround is slow. It's a document-reasoning problem sitting on top of a high-stakes decision — exactly the kind of thing where a naive LLM will confidently hallucinate a policy clause that doesn't exist.

CareGuard treats the **guardrails as the product**, not an afterthought. The interesting engineering isn't "can an LLM read a policy" — it's "can the system prove *which clause* it relied on, admit when it's unsure, and be monitored in production like any other ML system."

---

## What it does

Given a synthetic PA request + supporting notes, CareGuard:

1. Retrieves the relevant medical-policy sections for the requested service.
2. Checks the case against the policy's coverage criteria, clause by clause.
3. Validates its own reasoning against the retrieved text to catch unsupported claims.
4. Returns a decision with a **confidence score**, a **cited rationale** (every claim points to a policy clause), and an **audit record**.
5. **Escalates to a human** whenever confidence is low or criteria are ambiguous.

---

## Architecture

CareGuard is built as a **LangGraph** state machine of specialized agents rather than one mega-prompt. Each node has one job, which makes the system testable and the reasoning inspectable.

```
                    ┌──────────────┐
   PA request  ───▶ │  Retriever   │  pulls relevant policy sections (vector search)
   + notes          └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │   Reasoner   │  maps case ↔ policy criteria, drafts rationale
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │Guardrail/    │  verifies every claim is grounded in retrieved text;
                    │Critic        │  flags hallucinations, scores confidence
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │   Router     │  confident → auto-decision
                    └──────┬───────┘  low-confidence/ambiguous → human review
                           ▼
              approve / deny / route-to-human
              + citations + confidence + audit log
```

| Agent | Responsibility |
|-------|----------------|
| **Retriever** | Semantic search over chunked policy docs; returns candidate clauses with source IDs |
| **Reasoner** | Evaluates the case against retrieved criteria, produces a structured draft rationale |
| **Guardrail / Critic** | Checks each rationale claim is supported by retrieved text; produces a grounding + confidence score |
| **Router** | Decides auto-resolve vs. escalate based on confidence and criteria coverage |

---

## Tech stack

- **Orchestration:** LangGraph
- **LLM:** pluggable — `mock` (deterministic, no key), OpenAI, or Ollama
- **Retrieval:** sentence-transformer embeddings + a numpy cosine index (FAISS/Chroma-shaped interface)
- **Data pipeline:** parse → clean → chunk; PySpark when installed, Python fallback otherwise
- **Storage:** SQLite audit trail (swap `storage/db.py` for Postgres)
- **Interface:** FastAPI backend + Streamlit demo UI + metrics dashboard
- **Evaluation / CI:** pytest + rule-based grounding grader + LLM-as-judge, gated in GitHub Actions

---

## Responsible-AI design

These aren't features bolted on at the end — they're the reason the architecture looks the way it does.

- **Citation grounding** — every claim in a rationale references the exact policy clause it used. No citation, no claim.
- **Abstention over guessing** — below a confidence threshold, the system routes to a human instead of forcing a decision.
- **Human-in-the-loop by default** — auto-decisions are the exception, not the rule; the router is tuned to escalate.
- **Auditability** — inputs, retrieved context, reasoning, and outputs are logged for every case.
- **Measured, not assumed** — grounding rate and hallucination rate are tracked as first-class metrics (see below).

---

## Evaluation & monitoring

CareGuard ships with an evaluation harness so LLM behavior is regression-tested like any other system, not eyeballed.

- A labeled set of **synthetic PA cases** with expected outcomes.
- **Grounding check:** does every cited clause actually exist in the source and support the claim?
- **Decision accuracy** against the labeled outcomes.
- **Escalation rate** and **latency**, tracked over time.
- Metrics rendered in a small dashboard and asserted in CI, so a prompt or model change that degrades grounding **fails the build**.

| Metric | What it tells you |
|--------|-------------------|
| Policy-grounding rate | % of claims traceable to a real, supporting clause |
| Hallucination rate | % of claims with no valid supporting clause |
| Decision accuracy | Agreement with labeled outcomes on auto-decided cases |
| Escalation rate | % of cases routed to a human |
| P95 latency | End-to-end response time |

---

## Getting started

```bash
# 1. Clone
git clone https://github.com/sajansshergill/careguard.git
cd careguard

# 2. Environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure (copy and fill in)
cp .env.example .env      # set LLM_PROVIDER, model, API key if using a hosted model

# 4. Build the policy index (downloads MiniLM embeddings on first run)
python -m careguard.ingest --source data/policies/
python -m careguard.ingest --source data/policies/

# 5. Run the demo
streamlit run app.py
```

Or: `make install && make ingest && make run`.

API: `make api` then `POST /triage`. Metrics: `make dashboard`.

### Run the evaluation

```bash
pytest tests/ -v                 # unit + grounding tests
python -m careguard.eval         # full harness → JSON + HTML report
```

---

## Project structure

```
careguard/
│
├── README.md                     # this file
├── LICENSE                       # MIT
├── requirements.txt              # pinned dependencies
├── .env.example                  # template for secrets/config (copy → .env)
├── .gitignore
├── pyproject.toml                # packaging + tool config (black, ruff, pytest)
├── Makefile                      # make ingest / eval / test / run shortcuts
├── docker-compose.yml            # optional: app + vector store + db
├── Dockerfile
│
├── app.py                        # Streamlit demo UI entrypoint
├── api.py                        # FastAPI service entrypoint
│
├── config/
│   ├── settings.py               # loads env vars, model + threshold config
│   ├── prompts/                  # versioned prompt templates (one file per agent)
│   │   ├── retriever.md
│   │   ├── reasoner.md
│   │   ├── guardrail.md
│   │   └── router.md
│   └── logging.yaml              # structured logging config
│
├── careguard/                    # main package
│   │
│   ├── __init__.py
│   ├── graph.py                  # LangGraph wiring: nodes, edges, state machine
│   ├── state.py                  # shared graph state schema (typed)
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py               # shared agent interface / LLM client wrapper
│   │   ├── retriever.py          # pulls relevant policy clauses (vector search)
│   │   ├── reasoner.py           # maps case ↔ criteria, drafts rationale
│   │   ├── guardrail.py          # grounding check + confidence scoring
│   │   └── router.py             # auto-decide vs. escalate logic
│   │
│   ├── ingest/                   # PySpark data pipeline
│   │   ├── __init__.py
│   │   ├── parse.py              # read raw policy PDFs / case JSON
│   │   ├── clean.py              # normalize, strip boilerplate
│   │   ├── chunk.py              # split policies into retrievable clauses
│   │   ├── embed.py              # embed chunks → vectors
│   │   └── build_index.py        # write vectors to the store (CLI: -m careguard.ingest)
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── vector_store.py       # FAISS/Chroma wrapper (add / query)
│   │   └── embeddings.py         # embedding model loader
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── db.py                 # SQLite/Postgres connection
│   │   ├── models.py             # case, decision, audit-log schemas
│   │   └── audit.py              # write/read audit trail
│   │
│   ├── eval/
│   │   ├── __init__.py
│   │   ├── harness.py            # runs cases → collects metrics (CLI: -m careguard.eval)
│   │   ├── graders/
│   │   │   ├── __init__.py
│   │   │   ├── grounding.py      # rule-based: does each cited clause exist + support?
│   │   │   ├── llm_judge.py      # LLM-as-judge scorer
│   │   │   └── accuracy.py       # compare vs. labeled outcomes
│   │   ├── metrics.py            # grounding rate, hallucination rate, escalation, latency
│   │   └── report.py             # renders metrics to console + JSON/HTML
│   │
│   └── utils/
│       ├── __init__.py
│       ├── citations.py          # clause-ID linking + citation formatting
│       ├── confidence.py         # confidence aggregation helpers
│       └── timing.py             # latency instrumentation
│
├── data/                         # NO PHI — synthetic + public only
│   ├── policies/                 # public coverage-policy source documents
│   ├── cases/
│   │   ├── synthetic_cases.json  # generated PA requests + notes
│   │   └── generate_cases.py     # script that produces the synthetic set
│   ├── labeled/
│   │   └── eval_set.json         # cases with expected outcomes for scoring
│   └── index/                    # built vector store (gitignored)
│
├── dashboards/
│   └── metrics_dashboard.py      # Streamlit view of eval metrics over time
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # fixtures (mock LLM, tiny index)
│   ├── unit/
│   │   ├── test_retriever.py
│   │   ├── test_reasoner.py
│   │   ├── test_guardrail.py
│   │   ├── test_router.py
│   │   └── test_citations.py
│   ├── integration/
│   │   ├── test_graph_end_to_end.py
│   │   └── test_ingest_pipeline.py
│   └── eval/
│       └── test_grounding_regression.py   # fails CI if grounding drops
│
├── notebooks/
│   ├── 01_explore_policies.ipynb
│   ├── 02_prototype_retrieval.ipynb
│   └── 03_eval_analysis.ipynb
│
├── scripts/
│   ├── setup_index.sh            # one-shot: ingest + build index
│   └── run_eval.sh               # one-shot: full eval + report
│
├── docs/
│   ├── architecture.md           # deeper design write-up
│   ├── responsible_ai.md         # guardrail + abstention rationale
│   └── diagrams/
│       └── agent_flow.png
│
└── .github/
    └── workflows/
        └── ci.yml                # lint + tests + grounding regression on every push
```

---

## Roadmap

- [x] Structured export of audit logs (`GET /audit`, `export_audit()`)
- [x] Mock / OpenAI / Ollama swap on the same agent graph
- [ ] Confidence calibration on the router threshold
- [ ] Batch mode for bulk case processing via PySpark
- [ ] Model-swap benchmark (hosted vs. local) on the eval harness

---

## Disclaimer

CareGuard is an independent educational project. It uses only synthetic data and publicly available documents, is not affiliated with any insurer, and must not be used for real coverage or clinical decisions.
