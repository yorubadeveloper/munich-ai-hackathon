---
estimated_steps: 7
estimated_files: 2
skills_used: []
---

# T01: Create synthetic data generator

Create `backend/eval/__init__.py` and `backend/eval/generator.py`.

The generator must:
1. Define a Pydantic model for a synthetic job posting with fields: `text` (raw posting text), `ground_truth` (dict mapping each of the 7 entity labels to expected extracted value).
2. Use Gemini Structured Outputs to generate 30-50 synthetic Tech/Startups job postings with ground truth annotations for: company_name, job_title, tech_stack, company_stage, hiring_manager, salary, remote_policy.
3. Save generated data to `backend/eval/data/synthetic_eval.json`.
4. Include a CLI entry point (`if __name__ == '__main__'`) so it can be run standalone with `uv run python -m eval.generator`.
5. Handle Gemini API errors gracefully (log and skip failed generations).

## Inputs

- `backend/tools/gemini_client.py`
- `backend/config.py`

## Expected Output

- `backend/eval/__init__.py`
- `backend/eval/generator.py`

## Verification

uv run python -c "from eval.generator import SyntheticJobPosting; print('import ok')"
