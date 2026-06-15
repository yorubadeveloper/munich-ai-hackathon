pytest_plugins = ("pytest_asyncio",)
import json
from unittest.mock import patch

import pytest

from eval.evaluator import EvalResult, run_evaluation

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def synthetic_data_path(tmp_path):
    data = [
        {
            "text": "Seeking a Senior Go Engineer at TechCorp. Remote role. $150k.",
            "ground_truth": {
                "company_name": "TechCorp",
                "job_title": "Senior Go Engineer",
                "tech_stack": "Go",
                "company_stage": "",
                "hiring_manager": "",
                "salary": "$150k",
                "remote_policy": "Remote"
            }
        }
    ]
    filepath = tmp_path / "test_data.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return str(filepath)


@pytest.mark.asyncio
async def test_run_evaluation(synthetic_data_path):
    with patch("eval.evaluator.extract_job_entities") as mock_pioneer, \
         patch("eval.evaluator.extract_via_gemini") as mock_gemini:

        # Pioneer gets everything perfectly
        mock_pioneer.return_value = {
            "company_name": "TechCorp",
            "job_title": "Senior Go Engineer",
            "tech_stack": "Go",
            "company_stage": "",
            "hiring_manager": "",
            "salary": "$150k",
            "remote_policy": "Remote"
        }

        # Gemini gets title wrong and misses salary
        mock_gemini.return_value = {
            "company_name": "TechCorp",
            "job_title": "Go Developer",
            "tech_stack": "Go",
            "company_stage": "",
            "hiring_manager": "",
            "salary": "",
            "remote_policy": "Remote"
        }

        result = await run_evaluation(synthetic_data_path)

        assert isinstance(result, EvalResult)
        assert result.sample_count == 1

        # Pioneer should have perfect 1.0 everywhere
        assert result.mean_f1_pioneer == 1.0
        for score in result.per_label_f1_pioneer.values():
            assert score == 1.0

        # Gemini should be lower
        assert result.mean_f1_gemini < 1.0
        assert result.per_label_f1_gemini["company_name"] == 1.0
        assert result.per_label_f1_gemini["salary"] == 0.0  # Missed completely
        assert result.per_label_f1_gemini["job_title"] > 0.0  # Partial overlap 'Go'
        assert result.per_label_f1_gemini["job_title"] < 1.0

        # Result schema matches what S03 needs
        data = result.model_dump()
        assert "per_label_f1_pioneer" in data
        assert "per_label_f1_gemini" in data
        assert "mean_f1_pioneer" in data
        assert "mean_f1_gemini" in data
        assert "sample_count" in data
        assert "fine_tuning_triggered" in data
