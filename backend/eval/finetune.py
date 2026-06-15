import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from eval.evaluator import EvalResult
from eval.generator import SyntheticJobPosting
from tools.gemini_client import _extract_json, _generate
from tools.gliner_client import submit_training_job

log = logging.getLogger(__name__)

class LifecycleStatus(BaseModel):
    status: str
    threshold: float
    mean_f1_pioneer: float
    job_id: Optional[str] = None
    degraded_reason: Optional[str] = None
    training_batch_path: Optional[str] = None
    timestamp: str

WEAK_LABEL_PROMPT = """
You are a technical recruiter creating varied job postings for Tech/Startup roles.
Generate a realistic job posting (200-500 words).
Ensure the job posting heavily emphasizes and explicitly includes clear details for the following weak labels:
{weak_labels}

Also naturally include the following standard labels if possible:
- company_name
- job_title
- tech_stack
- company_stage
- hiring_manager
- salary
- remote_policy

Return ONLY a JSON object containing two keys:
- "text": The full text of the job posting.
- "ground_truth": A dictionary mapping the 7 entity labels (exactly as written above) to the string value found in the text.
If an entity is intentionally omitted, set its ground_truth value to "".
Do not include any other markdown formatting outside of the JSON block.
"""

async def generate_targeted_posting(weak_labels: List[str]) -> Optional[SyntheticJobPosting]:
    try:
        prompt = WEAK_LABEL_PROMPT.format(weak_labels=", ".join(weak_labels))
        response_text = await _generate(prompt)
        parsed = _extract_json(response_text)

        if "text" in parsed and "ground_truth" in parsed:
            required_keys = ["company_name", "job_title", "tech_stack", "company_stage", "hiring_manager", "salary", "remote_policy"]
            for k in required_keys:
                if k not in parsed["ground_truth"]:
                    parsed["ground_truth"][k] = ""
            return SyntheticJobPosting(text=parsed["text"], ground_truth=parsed["ground_truth"])
        return None
    except Exception as e:
        log.warning(f"Failed to generate targeted posting: {e}")
        return None

async def generate_training_batch(weak_labels: List[str], num_items: int = 10) -> List[SyntheticJobPosting]:
    log.info(f"Generating training batch of {num_items} items focused on {weak_labels}...")
    tasks = [generate_targeted_posting(weak_labels) for _ in range(num_items)]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]

async def run_finetuning_pipeline(eval_result: EvalResult, threshold: float = 0.8) -> LifecycleStatus:
    timestamp = datetime.now(timezone.utc).isoformat()

    if eval_result.mean_f1_pioneer >= threshold:
        log.info(f"Mean F1 ({eval_result.mean_f1_pioneer:.4f}) >= threshold ({threshold}). Skipping fine-tuning.")
        return LifecycleStatus(
            status="skipped_threshold_met",
            threshold=threshold,
            mean_f1_pioneer=eval_result.mean_f1_pioneer,
            timestamp=timestamp
        )

    log.info(f"Mean F1 ({eval_result.mean_f1_pioneer:.4f}) < threshold ({threshold}). Triggering fine-tuning.")

    # Identify weak labels (e.g. bottom 3)
    sorted_labels = sorted(eval_result.per_label_f1_pioneer.items(), key=lambda x: x[1])
    weak_labels = [label for label, score in sorted_labels[:3]]

    # Generate training batch
    batch = await generate_training_batch(weak_labels, num_items=10)

    # Save training batch
    batch_path = os.path.join(os.path.dirname(__file__), "data", "synthetic_train.json")
    Path(batch_path).parent.mkdir(parents=True, exist_ok=True)
    with open(batch_path, "w", encoding="utf-8") as f:
        json.dump([item.model_dump() for item in batch], f, indent=2)

    # Prepare data for submission
    # We need to map SyntheticJobPosting to the Pioneer expected format (list of dicts)
    # Pioneer schema: {"text": str, "labels": {"label_name": ["value"]}}
    training_data = []
    for item in batch:
        labels_dict = {}
        for label, val in item.ground_truth.items():
            if val:
                labels_dict[label] = [val]
        training_data.append({
            "text": item.text,
            "labels": labels_dict
        })

    # Submit job
    status, job_id, error = await submit_training_job(training_data)

    lifecycle = LifecycleStatus(
        status=status,
        threshold=threshold,
        mean_f1_pioneer=eval_result.mean_f1_pioneer,
        job_id=job_id,
        degraded_reason=error,
        training_batch_path=batch_path,
        timestamp=datetime.now(timezone.utc).isoformat()
    )

    lifecycle_path = os.path.join(os.path.dirname(__file__), "data", "lifecycle.json")
    with open(lifecycle_path, "w", encoding="utf-8") as f:
        f.write(lifecycle.model_dump_json(indent=2))

    log.info(f"Fine-tuning pipeline completed with status: {status}")
    return lifecycle
