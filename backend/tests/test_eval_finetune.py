from unittest.mock import patch

import pytest

from eval.evaluator import EvalResult
from eval.finetune import run_finetuning_pipeline

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def base_eval_result():
    return EvalResult(
        per_label_f1_pioneer={"company_name": 0.9, "job_title": 0.5, "salary": 0.6},
        per_label_f1_gemini={"company_name": 0.9, "job_title": 0.9, "salary": 0.9},
        mean_f1_pioneer=0.6,
        mean_f1_gemini=0.9,
        sample_count=10,
        fine_tuning_triggered=True
    )


@pytest.mark.asyncio
async def test_skip_finetuning_on_high_f1(base_eval_result):
    base_eval_result.mean_f1_pioneer = 0.9

    with patch("eval.finetune.generate_training_batch") as mock_generate:
        result = await run_finetuning_pipeline(base_eval_result, threshold=0.8)

        assert result.status == "skipped_threshold_met"
        assert result.mean_f1_pioneer == 0.9
        mock_generate.assert_not_called()


@pytest.mark.asyncio
async def test_trigger_finetuning_on_low_f1(base_eval_result):
    from eval.generator import SyntheticJobPosting

    mock_batch = [
        SyntheticJobPosting(text="Job", ground_truth={"job_title": "Engineer"})
    ]

    with patch("eval.finetune.generate_training_batch", return_value=mock_batch) as mock_generate, \
         patch("eval.finetune.submit_training_job", return_value=("submitted", "job_123", None)) as mock_submit:

        result = await run_finetuning_pipeline(base_eval_result, threshold=0.8)

        assert result.status == "submitted"
        assert result.job_id == "job_123"
        assert result.degraded_reason is None
        mock_generate.assert_called_once()
        mock_submit.assert_called_once()


@pytest.mark.asyncio
async def test_graceful_degradation_on_api_failure(base_eval_result):
    from eval.generator import SyntheticJobPosting

    mock_batch = [
        SyntheticJobPosting(text="Job", ground_truth={"job_title": "Engineer"})
    ]

    with patch("eval.finetune.generate_training_batch", return_value=mock_batch), \
         patch("eval.finetune.submit_training_job", return_value=("failed", None, "API returned 500")) as mock_submit:

        result = await run_finetuning_pipeline(base_eval_result, threshold=0.8)

        assert result.status == "failed"
        assert result.job_id is None
        assert result.degraded_reason == "API returned 500"
        mock_submit.assert_called_once()
