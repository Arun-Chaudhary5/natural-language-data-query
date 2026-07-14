# Benchmark Results Summary

> **WARNING**: Incomplete run! Only 3 out of 200 cases were evaluated.

## Overall Metrics
- **Total Cases Evaluated**: 3
- **Providers**: gemini
- **Models**: gemini-2.5-flash
- **Success Rate**: 100.0% (3/3)
- **Exact Match Accuracy**: 33.33%
- **Execution Match Accuracy**: 66.67%

### Latency & Retries
- **Average Latency**: 1497.16 ms
- **P50 Latency**: 1666.62 ms
- **P95 Latency**: 1839.91 ms
- **Average Retries**: 0.0 (Total: 0)

### Failure Breakdown
- **Validation Failures**: 0
- **Execution Failures**: 0
- **Generation/Other Failures**: 0

## Category Breakdown
| Category | Total | Success Rate | Exact Match | Execution Match |
|---|---|---|---|---|
| basic | 3 | 100.0% | 33.33% | 66.67% |


## Failure Examples
### Example 1 (ID: 3)
**Question**: Show all products costing more than 10000.

**Expected SQL**:
```sql
SELECT * FROM products WHERE price > 10000;
```

**Predicted SQL**:
```sql
SELECT product_name FROM products WHERE price > 10000
```

**Reason**: Valid SQL but incorrect execution result.
