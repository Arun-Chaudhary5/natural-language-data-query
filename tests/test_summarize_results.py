import pytest
from benchmark.summarize_results import calculate_metrics

def test_calculate_metrics():
    records = [
        {
            "id": 1,
            "success": True,
            "exact_match": True,
            "execution_match": True,
            "latency_ms": 100,
            "retry_count": 0,
            "error": None,
            "provider": "gemini",
            "model": "gemini-2.5-flash"
        },
        {
            "id": 2,
            "success": True,
            "exact_match": False,
            "execution_match": True,
            "latency_ms": 200,
            "retry_count": 1,
            "error": None,
            "provider": "gemini",
            "model": "gemini-2.5-flash"
        },
        {
            "id": 3,
            "success": False,
            "exact_match": False,
            "execution_match": False,
            "latency_ms": 300,
            "retry_count": 0,
            "error": "SQL validation failed: Rejecting DELETE",
            "provider": "gemini",
            "model": "gemini-2.5-flash"
        }
    ]

    metrics = calculate_metrics(records)

    assert metrics["total"] == 3
    assert metrics["successful"] == 2
    assert metrics["exact_matches"] == 1
    assert metrics["execution_matches"] == 2
    
    # latencies: 100, 200, 300
    assert metrics["latencies"]["average_ms"] == 200.0
    assert metrics["latencies"]["p50_ms"] == 200.0
    assert metrics["latencies"]["p95_ms"] >= 200.0  # Just ensure it's calculated
    
    assert metrics["retries"]["total"] == 1
    assert metrics["retries"]["average"] == round(1/3, 2)
    
    assert metrics["errors"]["validation"] == 1
    assert metrics["errors"]["execution"] == 0
    assert metrics["errors"]["generation"] == 0

    assert len(metrics["failure_examples"]) == 1
    assert metrics["failure_examples"][0]["id"] == 3
