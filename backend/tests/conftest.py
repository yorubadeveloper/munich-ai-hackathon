from tests.fixtures.evidence import (
    company_uuid,
    fal_evidence,
    gemini_evidence,
    partial_failure_evidence,
    pioneer_evidence,
    tavily_evidence,
    telegram_evidence,
)

pytest_plugins = [
    "pytest_mock",
]

__all__ = [
    "company_uuid",
    "fal_evidence",
    "gemini_evidence",
    "partial_failure_evidence",
    "pioneer_evidence",
    "tavily_evidence",
    "telegram_evidence",
]
