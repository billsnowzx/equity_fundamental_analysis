"""Tests for orchestration service helpers."""

from __future__ import annotations

import socket

from src.orchestration.service import classify_runtime_failure, determine_report_eligibility
from src.providers.errors import ProviderConfigurationError, ProviderDataError


def test_classify_runtime_failure_for_provider_configuration() -> None:
    category, message = classify_runtime_failure(ProviderConfigurationError("missing token"))

    assert category == "configuration"
    assert message == "missing token"


def test_classify_runtime_failure_for_provider_data() -> None:
    category, message = classify_runtime_failure(ProviderDataError("missing annual data"))

    assert category == "data"
    assert message == "missing annual data"


def test_classify_runtime_failure_for_timeout() -> None:
    category, message = classify_runtime_failure(socket.timeout("timed out"))

    assert category == "network"
    assert "Timed out" in message


def test_determine_report_eligibility_accepts_matching_success() -> None:
    eligible, reason = determine_report_eligibility(
        {
            "status": "success",
            "overall_score": 81.5,
            "red_flag_count": 1,
            "overall_label": "high-quality compounder",
        },
        minimum_score=80.0,
        max_red_flags=2,
        allowed_labels={"high-quality compounder"},
    )

    assert eligible is True
    assert reason is None


def test_determine_report_eligibility_rejects_unselected_label() -> None:
    eligible, reason = determine_report_eligibility(
        {
            "status": "success",
            "overall_score": 81.5,
            "red_flag_count": 1,
            "overall_label": "good business, too expensive",
        },
        allowed_labels={"high-quality compounder"},
    )

    assert eligible is False
    assert reason == "label_not_selected"
