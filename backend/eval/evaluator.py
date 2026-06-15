import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Dict

from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eval.generator import SyntheticJobPosting
from eval.metrics import compute_mean_f1, compute_per_label_f1
from tools.gemini_client import _extract_json, _generate
from tools.gliner_client import JOB_ENTITY_LABELS, extract_job_entities

log = logging.getLogger(__name__)

class EvalResult(BaseModel):
    per_label_f1_pioneer: Dict[str, float]
    per_label_f1_gemini: Dict[str, float]
    mean_f1_pioneer: float
    mean_f1_gemini: float
    sample_count: int
    fine_tuning_triggered: bool


GEMINI_EXTRACTION_PROMPT = """
Extract the following entities from the job posting text below.
Entities to extract:
- company_name
- job_title
- tech_stack
- company_stage
- hiring_manager
- salary
- remote_policy

Return ONLY a JSON object mapping these labels to their extracted string values.
If an entity is not found, map its label to an empty string "".

Job Posting Text:
{text}
"""

async def extract_via_gemini(text: str) -> Dict[str, str]:
    try:
        prompt = GEMINI_EXTRACTION_PROMPT.format(text=text)
        response_text = await _generate(prompt)
        parsed = _extract_json(response_text)

        result = {}
        for label in JOB_ENTITY_LABELS:
            result[label] = str(parsed.get(label, ""))
        return result
    except Exception as e:
        log.warning(f"Failed Gemini extraction: {e}")
        return {label: "" for label in JOB_ENTITY_LABELS}


async def evaluate_posting(posting: SyntheticJobPosting) -> tuple[Dict[str, float], Dict[str, float]]:
    text = posting.text
    ground_truth = posting.ground_truth

    # Run extractions concurrently
    pioneer_task = extract_job_entities(text)
    gemini_task = extract_via_gemini(text)

    pioneer_pred, gemini_pred = await asyncio.gather(pioneer_task, gemini_task)

    pioneer_f1 = compute_per_label_f1(pioneer_pred, ground_truth, JOB_ENTITY_LABELS)
    gemini_f1 = compute_per_label_f1(gemini_pred, ground_truth, JOB_ENTITY_LABELS)

    return pioneer_f1, gemini_f1


async def run_evaluation(data_path: str) -> EvalResult:
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            postings = [SyntheticJobPosting(**p) for p in data]
    except Exception as e:
        log.error(f"Failed to load synthetic data from {data_path}: {e}")
        raise

    sample_count = len(postings)
    if sample_count == 0:
        raise ValueError("No samples found in data.")

    log.info(f"Evaluating {sample_count} postings...")

    tasks = [evaluate_posting(p) for p in postings]
    results = await asyncio.gather(*tasks)

    # Aggregate results
    sum_pioneer_f1 = {label: 0.0 for label in JOB_ENTITY_LABELS}
    sum_gemini_f1 = {label: 0.0 for label in JOB_ENTITY_LABELS}

    for p_f1, g_f1 in results:
        for label in JOB_ENTITY_LABELS:
            sum_pioneer_f1[label] += p_f1[label]
            sum_gemini_f1[label] += g_f1[label]

    avg_pioneer_f1 = {label: score / sample_count for label, score in sum_pioneer_f1.items()}
    avg_gemini_f1 = {label: score / sample_count for label, score in sum_gemini_f1.items()}

    mean_f1_pioneer = compute_mean_f1(avg_pioneer_f1)
    mean_f1_gemini = compute_mean_f1(avg_gemini_f1)

    # Simple logic for fine-tuning trigger based on Pioneer performance (placeholder or could be config-driven)
    # E.g. If pioneer mean F1 is less than 0.8, trigger fine-tuning
    fine_tuning_triggered = mean_f1_pioneer < 0.8

    eval_result = EvalResult(
        per_label_f1_pioneer=avg_pioneer_f1,
        per_label_f1_gemini=avg_gemini_f1,
        mean_f1_pioneer=mean_f1_pioneer,
        mean_f1_gemini=mean_f1_gemini,
        sample_count=sample_count,
        fine_tuning_triggered=fine_tuning_triggered
    )

    log.info("\nEvaluation Results:")
    log.info(f"Sample Count: {sample_count}")
    log.info("Pioneer F1 Scores:")
    for label, score in avg_pioneer_f1.items():
        log.info(f"  {label}: {score:.4f}")
    log.info(f"  Mean: {mean_f1_pioneer:.4f}")

    log.info("\nGemini F1 Scores:")
    for label, score in avg_gemini_f1.items():
        log.info(f"  {label}: {score:.4f}")
    log.info(f"  Mean: {mean_f1_gemini:.4f}")

    return eval_result


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Evaluate Pioneer vs Gemini extraction")
    default_data_path = os.path.join(os.path.dirname(__file__), "data", "synthetic_eval.json")
    parser.add_argument("--data", default=default_data_path, help="Path to synthetic eval JSON")
    args = parser.parse_args()

    result = asyncio.run(run_evaluation(args.data))
    # Print a clear summary
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
