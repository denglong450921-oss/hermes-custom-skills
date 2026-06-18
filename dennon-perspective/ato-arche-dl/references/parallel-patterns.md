# Parallel Execution Patterns

## When to Parallelize

Run steps in parallel when:
- No data dependency between them (step B doesn't need step A's output)
- Each step is I/O-bound (network calls, file reads, API queries)
- Failure in one doesn't invalidate the others
- Cost of parallel execution < cost of sequential wait time

Don't parallelize when:
- Steps have strict ordering (parse → transform → validate)
- Shared mutable state (writing to same file, same DB row)
- Rate limits would be exceeded (API throttling)
- Debugging becomes impossible (logs interleave, errors hard to trace)

## Pattern 1: Fan-Out / Fan-In

```
[Orchestrator]
    |
    +---> [skill-A] --->+
    |                    |
    +---> [skill-B] --->+---> [aggregate]
    |                    |
    +---> [skill-C] --->+
```

**Use when:** Multiple items need the same processing (batch OCR, parallel API calls, multi-file transforms).

**Contract requirements:**
- Each parallel skill gets independent input (no shared state)
- Aggregator skill defines timeout and partial-result policy
- Failure in one branch doesn't cancel others (unless explicitly configured)

**Example:** Processing 50 images → fan out 50 `image-ocr` calls → fan in to `merge-results`.

## Pattern 2: Pipeline Stages with Buffers

```
[stage-1] --> [buffer] --> [stage-2] --> [buffer] --> [stage-3]
```

**Use when:** Streaming data through transformations (log processing, real-time transcription).

**Contract requirements:**
- Each stage defines input/output schema
- Buffers handle backpressure (stage-2 slower than stage-1)
- Checkpoint after each stage for resume capability

**Example:** Video → `extract-audio` → buffer → `transcribe` → buffer → `polish-text`.

## Pattern 3: Competitive Execution

```
[Orchestrator]
    |
    +---> [skill-fast-expensive] ---+
    |                                |
    +---> [skill-slow-cheap] --------+---> [pick-first-success]
```

**Use when:** Multiple implementations exist with different cost/latency tradeoffs.

**Contract requirements:**
- All skills produce same output schema
- Orchestrator defines selection policy (first success, cheapest success, highest quality)
- Cancel losers when winner emerges (avoid wasted compute)

**Example:** `transcribe-gpu` (fast, $0.10/min) vs `transcribe-cpu` (slow, $0.02/min) → pick first to complete.

## Cost Budgeting

### Token/Credit Budgets

Add budget constraints to orchestration contracts:

```json
{
  "max_tokens": 50000,
  "max_api_calls": 100,
  "max_wall_time_seconds": 300,
  "on_budget_exceeded": "stop_and_report | use_cheaper_fallback | partial_result"
}
```

**Monitoring:**
- Track cumulative cost per `run_id`
- Check budget before each step
- Log budget consumption for post-mortem analysis

### Adaptive Routing

Route based on estimated cost:

```
if item_count < 10:
    use_expensive_high_quality_skill
elif item_count < 100:
    use_balanced_skill
else:
    use_cheap_bulk_skill
```

## Checkpoint Strategy

### What to Checkpoint

Checkpoint when:
- Step is expensive (API calls, GPU time)
- Step is slow (> 1 minute)
- Step is failure-prone (network requests, model calls)
- Partial results have value (user can inspect intermediate output)

### Checkpoint Schema

```json
{
  "run_id": "uuid",
  "step_name": "collect-works",
  "status": "completed | failed | partial",
  "output_ref": "s3://bucket/path | /local/path",
  "timestamp": "ISO8601",
  "cost_so_far": 0.45,
  "tokens_used": 12500
}
```

### Resume Protocol

On resume:
1. Load checkpoint for `run_id`
2. Verify checkpoint output still exists (file not deleted, API token still valid)
3. Skip completed steps
4. Continue from `failed` or `partial` step
5. If checkpoint invalid, restart from beginning and log warning

## Idempotency

### Idempotent Steps

A step is idempotent if running it twice produces the same result as running it once.

**Examples:**
- Download file to specific path (overwrite)
- Write to DB with upsert (INSERT ... ON CONFLICT UPDATE)
- Call API with `If-None-Match` header

**Non-idempotent examples:**
- Append to log file (duplicates on retry)
- Send email (sends twice on retry)
- Increment counter (double-counts on retry)

### Making Steps Idempotent

**Pattern: Idempotency Key**

```python
idempotency_key = hash(input_params + run_id + step_name)
# Pass to API, DB, or file system
# Server checks if key already processed
```

**Pattern: Conditional Write**

```python
# Only write if not already exists
if not os.path.exists(output_path):
    write_output(output_path)
```

## Failure Isolation

### Bulkhead Pattern

Isolate failures so one bad branch doesn't crash the workflow:

```
[Orchestrator]
    |
    +---> [skill-A] (timeout: 30s, retry: 2) ---> if fail: log_error, continue
    |
    +---> [skill-B] (timeout: 30s, retry: 2) ---> if fail: log_error, continue
    |
    +---> [skill-C] (timeout: 30s, retry: 2) ---> if fail: log_error, continue
```

**Contract:** Each parallel branch has independent timeout, retry count, and failure handler.

### Circuit Breaker

Stop calling a failing service after N failures:

```
if failure_count > threshold:
    skip_step(reason="circuit_open")
    wait(cooldown_period)
    retry_with_fallback_skill
```

## Practical Example: Batch Image Processing

```json
{
  "orchestration": {
    "step_0": {
      "invoke": "health-check",
      "input": "runtime_context",
      "output": "health_status"
    },
    "step_1": {
      "invoke": "parse-manifest",
      "input": "user_input.manifest_url",
      "output": "image_list[]"
    },
    "step_2": {
      "invoke": "image-ocr",
      "input": "image_list[]",
      "execution": "parallel",
      "max_concurrency": 10,
      "timeout_per_item": 60,
      "on_partial_failure": "continue_with_successful_items",
      "checkpoint": true,
      "output": "ocr_results[]"
    },
    "step_3": {
      "invoke": "aggregate-results",
      "input": "ocr_results[]",
      "output": "final_report",
      "budget": {
        "max_tokens": 100000,
        "on_exceeded": "partial_result"
      }
    }
  }
}
```
