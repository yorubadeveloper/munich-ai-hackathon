import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# Add the parent directory of 'eval' to PYTHONPATH if running as script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.gemini_client import _extract_json, _generate

log = logging.getLogger(__name__)

class SyntheticJobPosting(BaseModel):
    text: str = Field(..., description="The raw generated text of the job posting")
    ground_truth: Dict[str, str] = Field(..., description="A dictionary containing the extracted entity labels")


GENERATION_PROMPT = """
You are a technical recruiter creating realistic, varied job postings for Tech/Startup roles.
Generate a single, realistic job posting (between 200 and 500 words).
Ensure the job posting includes clear details for the following 7 entities, although they don't have to be explicitly labeled in the text (they should feel natural):
- company_name
- job_title
- tech_stack (comma separated list of technologies)
- company_stage (e.g. Seed, Series A, Public)
- hiring_manager (name of the person)
- salary (a range or specific amount)
- remote_policy (e.g. Remote, Hybrid, On-site)

Return ONLY a JSON object containing two keys:
- "text": The full text of the job posting.
- "ground_truth": A dictionary mapping the 7 entity labels (exactly as written above) to the string value found in the text.

If an entity is intentionally omitted from the text to simulate a realistic incomplete posting, set its ground_truth value to "".
Do not include any other markdown formatting outside of the JSON block.
"""

async def generate_posting() -> Optional[SyntheticJobPosting]:
    try:
        response_text = await _generate(GENERATION_PROMPT)
        parsed = _extract_json(response_text)

        if "text" in parsed and "ground_truth" in parsed:
            # Ensure all required keys exist in ground_truth
            required_keys = ["company_name", "job_title", "tech_stack", "company_stage", "hiring_manager", "salary", "remote_policy"]
            for k in required_keys:
                if k not in parsed["ground_truth"]:
                    parsed["ground_truth"][k] = ""

            return SyntheticJobPosting(text=parsed["text"], ground_truth=parsed["ground_truth"])
        else:
            log.warning("Generated JSON missing required keys.")
            return None
    except Exception as e:
        log.warning(f"Failed to generate synthetic posting: {e}")
        return None

async def generate_dataset(num_postings: int = 30) -> List[SyntheticJobPosting]:
    log.info(f"Generating {num_postings} synthetic job postings...")
    tasks = [generate_posting() for _ in range(num_postings)]
    results = await asyncio.gather(*tasks)

    valid_results = [r for r in results if r is not None]
    log.info(f"Successfully generated {len(valid_results)} postings.")
    return valid_results

def save_dataset(dataset: List[SyntheticJobPosting], filepath: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    data = [posting.model_dump() for posting in dataset]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log.info(f"Saved dataset to {filepath}")

async def main():
    logging.basicConfig(level=logging.INFO)
    dataset = await generate_dataset(30)
    save_path = os.path.join(os.path.dirname(__file__), "data", "synthetic_eval.json")
    save_dataset(dataset, save_path)

if __name__ == "__main__":
    asyncio.run(main())
