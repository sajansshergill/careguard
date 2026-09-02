.PHONY: install ingest cases eval test run api dashboard lint fmt

install:
	pip install -r requirements.txt
	pip install -e .

ingest:
	python -m careguard.ingest --source data/policies/

cases:
	python data/cases/generate_cases.py

eval:
	python -m careguard.eval

test:
	LLM_PROVIDER=mock pytest

run:
	streamlit run app.py

api:
	uvicorn api:app --reload

dashboard:
	streamlit run dashboards/metrics_dashboard.py

lint:
	ruff check .

fmt:
	black . && ruff check --fix .
