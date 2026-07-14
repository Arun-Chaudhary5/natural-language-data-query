import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
DATASET_PATH = Path(__file__).parent / "dataset.json"


def load_dataset_count():
    try:
        with DATASET_PATH.open("r", encoding="utf-8") as file:
            return len(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_results(path):
    records = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def percentage(value, total):
    if total == 0:
        return 0.0
    return round((value / total) * 100, 2)


def calculate_metrics(records):
    total = len(records)
    if total == 0:
        return {"total": 0}

    successful = sum(record.get("success", False) for record in records)
    exact_matches = sum(record.get("exact_match", False) for record in records)
    execution_matches = sum(record.get("execution_match", False) for record in records)

    latencies = sorted(record.get("latency_ms", 0) for record in records)
    average_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
    p50_latency = round(statistics.median(latencies), 2) if latencies else 0.0
    
    p95_latency = 0.0
    if latencies:
        if len(latencies) > 1:
            try:
                p95_latency = round(statistics.quantiles(latencies, n=100)[94], 2)
            except statistics.StatisticsError:
                p95_latency = max(latencies)
        else:
            p95_latency = max(latencies)

    total_retries = sum(record.get("retry_count", 0) for record in records)
    average_retries = round(total_retries / total, 2) if total else 0.0

    validation_failures = 0
    execution_failures = 0
    generation_failures = 0

    failures = []

    for record in records:
        err = str(record.get("error") or "")
        
        is_failure = False
        if not record.get("success"):
            is_failure = True
            if "SQL validation failed" in err or "SQLValidationError" in err:
                validation_failures += 1
            elif "SQL execution failed" in err or "SQLExecutionError" in err:
                execution_failures += 1
            else:
                generation_failures += 1
        elif not record.get("execution_match"):
            is_failure = True
            
        if is_failure:
            failures.append({
                "id": record.get("id"),
                "question": record.get("question"),
                "expected_sql": record.get("expected_sql"),
                "predicted_sql": record.get("predicted_sql"),
                "error": record.get("error"),
                "execution_match": record.get("execution_match", False)
            })

    providers = list(set(r.get("provider", "unknown") for r in records))
    models = list(set(r.get("model", "unknown") for r in records))

    return {
        "metadata": {
            "providers": providers,
            "models": models,
        },
        "total": total,
        "successful": successful,
        "success_rate": percentage(successful, total),
        "exact_matches": exact_matches,
        "exact_match_accuracy": percentage(exact_matches, total),
        "execution_matches": execution_matches,
        "execution_match_accuracy": percentage(execution_matches, total),
        "latencies": {
            "average_ms": average_latency,
            "p50_ms": p50_latency,
            "p95_ms": p95_latency,
        },
        "retries": {
            "total": total_retries,
            "average": average_retries,
        },
        "errors": {
            "validation": validation_failures,
            "execution": execution_failures,
            "generation": generation_failures,
        },
        "failure_examples": failures[:3],
    }


def group_by_category(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[record["category"]].append(record)
    return grouped


def print_metrics(title, metrics):
    print(title)
    print(f"Cases: {metrics['total']}")
    print(f"Successful executions: {metrics['successful']} ({metrics.get('success_rate', 0)}%)")
    print(f"Exact matches: {metrics.get('exact_matches', 0)} ({metrics.get('exact_match_accuracy', 0)}%)")
    print(f"Execution matches: {metrics.get('execution_matches', 0)} ({metrics.get('execution_match_accuracy', 0)}%)")
    
    if "latencies" in metrics:
        print(f"Average latency: {metrics['latencies']['average_ms']} ms")
        print(f"P50 latency: {metrics['latencies']['p50_ms']} ms")
        print(f"P95 latency: {metrics['latencies']['p95_ms']} ms")


def generate_markdown_report(summary, expected_total, path):
    overall = summary.get("overall", {})
    categories = summary.get("categories", {})
    
    md = []
    md.append("# Benchmark Results Summary\n")
    
    actual_total = overall.get('total', 0)
    if expected_total and actual_total < expected_total:
        md.append(f"> **WARNING**: Incomplete run! Only {actual_total} out of {expected_total} cases were evaluated.\n")
    elif expected_total and actual_total == expected_total:
        md.append(f"> **SUCCESS**: All {expected_total} cases were evaluated.\n")
        
    md.append("## Overall Metrics")
    md.append(f"- **Total Cases Evaluated**: {actual_total}")
    md.append(f"- **Providers**: {', '.join(overall.get('metadata', {}).get('providers', []))}")
    md.append(f"- **Models**: {', '.join(overall.get('metadata', {}).get('models', []))}")
    md.append(f"- **Success Rate**: {overall.get('success_rate')}% ({overall.get('successful')}/{actual_total})")
    md.append(f"- **Exact Match Accuracy**: {overall.get('exact_match_accuracy')}%")
    md.append(f"- **Execution Match Accuracy**: {overall.get('execution_match_accuracy')}%\n")
    
    md.append("### Latency & Retries")
    lats = overall.get('latencies', {})
    md.append(f"- **Average Latency**: {lats.get('average_ms')} ms")
    md.append(f"- **P50 Latency**: {lats.get('p50_ms')} ms")
    md.append(f"- **P95 Latency**: {lats.get('p95_ms')} ms")
    retries = overall.get('retries', {})
    md.append(f"- **Average Retries**: {retries.get('average')} (Total: {retries.get('total')})\n")
    
    md.append("### Failure Breakdown")
    errors = overall.get('errors', {})
    md.append(f"- **Validation Failures**: {errors.get('validation')}")
    md.append(f"- **Execution Failures**: {errors.get('execution')}")
    md.append(f"- **Generation/Other Failures**: {errors.get('generation')}\n")
    
    md.append("## Category Breakdown")
    md.append("| Category | Total | Success Rate | Exact Match | Execution Match |")
    md.append("|---|---|---|---|---|")
    for cat, c_metrics in categories.items():
        md.append(f"| {cat} | {c_metrics.get('total')} | {c_metrics.get('success_rate')}% | {c_metrics.get('exact_match_accuracy')}% | {c_metrics.get('execution_match_accuracy')}% |")
    md.append("\n")
    
    failures = overall.get("failure_examples", [])
    if failures:
        md.append("## Failure Examples")
        for idx, f in enumerate(failures, 1):
            md.append(f"### Example {idx} (ID: {f.get('id')})")
            md.append(f"**Question**: {f.get('question')}\n")
            md.append(f"**Expected SQL**:\n```sql\n{f.get('expected_sql')}\n```\n")
            md.append(f"**Predicted SQL**:\n```sql\n{f.get('predicted_sql')}\n```\n")
            if f.get('error'):
                md.append(f"**Error**: {f.get('error')}\n")
            if not f.get('execution_match') and not f.get('error'):
                md.append(f"**Reason**: Valid SQL but incorrect execution result.\n")
    
    with path.open("w", encoding="utf-8") as file:
        file.write("\n".join(md))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="benchmark_results.jsonl")
    parser.add_argument("--json-output", default="benchmark_summary.json")
    parser.add_argument("--md-output", default="benchmark_summary.md")
    args = parser.parse_args()

    results_path = RESULTS_DIR / args.input
    summary_path = RESULTS_DIR / args.json_output
    md_path = RESULTS_DIR / args.md_output

    records = load_results(results_path)
    if not records:
        raise SystemExit("No benchmark results found.")

    expected_total = load_dataset_count()
    overall_metrics = calculate_metrics(records)
    grouped = group_by_category(records)

    category_metrics = {
        category: calculate_metrics(category_records)
        for category, category_records in grouped.items()
    }

    summary = {
        "overall": overall_metrics,
        "categories": category_metrics,
        "expected_total_cases": expected_total
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with summary_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    generate_markdown_report(summary, expected_total, md_path)

    print()
    if expected_total and overall_metrics["total"] < expected_total:
        print(f"WARNING: Incomplete run. {overall_metrics['total']}/{expected_total} evaluated.\n")

    print_metrics("OVERALL RESULTS", overall_metrics)

    print("\nCATEGORY RESULTS")
    for category, metrics in category_metrics.items():
        print()
        print_metrics(category.upper(), metrics)

    print()
    print(f"JSON Summary saved to: {summary_path}")
    print(f"Markdown Report saved to: {md_path}")


if __name__ == "__main__":
    main()