# Real-World Pitfalls in Atomic + Orchestration Workflows

Lessons from production deployments. Each pitfall includes the symptom, root cause, and fix.

## Pitfall 1: The "God Skill" Creep

**Symptom:** One atomic skill grows to 500+ lines, handles 5+ responsibilities, and is called by every workflow.

**Root cause:** Started as a simple skill, then added "just one more feature" repeatedly. No one wanted to split it because "it works."

**Fix:**
1. List all responsibilities (actions that could be tested independently)
2. Split into N atomic skills, one per responsibility
3. Add an orchestration skill that coordinates them
4. Deprecate the god skill (keep it for backward compatibility, but don't use in new workflows)

**Prevention:** Review skill size monthly. If > 200 lines or > 3 responsibilities, split it.

## Pitfall 2: Implicit State Sharing

**Symptom:** Skill B fails because it expects a file that Skill A was supposed to create, but the file path is hardcoded or guessed.

**Root cause:** Skills share state through the filesystem or environment variables, but the contract doesn't specify the path or variable name.

**Fix:**
1. Make all state explicit in contracts
2. Orchestrator passes file paths as input parameters
3. Skills read from input parameters, not hardcoded paths

**Example:**
```
Bad:
  Skill A writes to /tmp/output.json
  Skill B reads from /tmp/output.json
  (What if Skill A runs on a different machine? What if /tmp is full?)

Good:
  Skill A output: {"output_path": "/tmp/run_123/output.json"}
  Orchestrator passes to Skill B: {"input_path": "/tmp/run_123/output.json"}
```

## Pitfall 3: Retry Storms

**Symptom:** API rate limit hit → retry immediately → rate limit hit again → retry → rate limit → ... (infinite loop)

**Root cause:** Retry logic doesn't use exponential backoff or respect rate-limit headers.

**Fix:**
1. Use exponential backoff: wait 1s, 2s, 4s, 8s, 16s between retries
2. Respect `Retry-After` headers from APIs
3. Set max retries (e.g., 5) and fail gracefully after that

**Example:**
```python
import time

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError as e:
            wait_time = e.retry_after or (2 ** attempt)
            time.sleep(wait_time)
    raise MaxRetriesExceeded(f"Failed after {max_retries} attempts")
```

## Pitfall 4: Silent Partial Failures

**Symptom:** Workflow completes "successfully" but output is missing 30% of expected items. No error logged.

**Root cause:** Parallel execution had some failures, but orchestrator only checked if at least one item succeeded.

**Fix:**
1. Track success/failure count for parallel steps
2. Define acceptable threshold (e.g., "at least 90% must succeed")
3. If below threshold, mark workflow as `partial` and report failures

**Example:**
```python
results = parallel_execute(items, skill_name)
success_count = sum(1 for r in results if r.status == "success")
failure_count = len(results) - success_count

if success_count / len(results) < 0.9:
    return {
        "status": "partial",
        "success_count": success_count,
        "failure_count": failure_count,
        "failures": [r for r in results if r.status == "failed"]
    }
```

## Pitfall 5: Checkpoint Corruption

**Symptom:** Workflow resumes from checkpoint, but checkpoint data is stale or corrupted. Workflow produces wrong output.

**Root cause:** Checkpoint was written, but then the underlying data changed (file deleted, API token expired, DB schema changed).

**Fix:**
1. Validate checkpoint before resuming
2. Check that referenced files still exist
3. Check that API tokens are still valid
4. If checkpoint invalid, restart from beginning and log warning

**Example:**
```python
def validate_checkpoint(checkpoint):
    # Check file exists
    if not os.path.exists(checkpoint["output_ref"]):
        return False, "Output file deleted"
    
    # Check file not corrupted
    try:
        with open(checkpoint["output_ref"]) as f:
            json.load(f)
    except json.JSONDecodeError:
        return False, "Output file corrupted"
    
    # Check API token still valid
    if not api_token_valid(checkpoint["api_token"]):
        return False, "API token expired"
    
    return True, "Checkpoint valid"
```

## Pitfall 6: Orchestrator Business Logic Leakage

**Symptom:** Orchestrator contains parsing rules, API payloads, or transformation logic. When business logic changes, you have to edit both the orchestrator and the atomic skill.

**Root cause:** "Quick fix" added logic to orchestrator instead of atomic skill. Over time, orchestrator becomes a second copy of business logic.

**Fix:**
1. Move all business logic to atomic skills
2. Orchestrator only contains: step sequence, routing logic, data flow, checkpoints
3. If orchestrator needs to transform data, create a `transform-data` atomic skill

**Prevention:** Code review rule: "If orchestrator has > 50 lines of non-routing logic, refactor."

## Pitfall 7: Contract Drift

**Symptom:** Skill A's output contract changed (added a field), but Skill B wasn't updated. Skill B fails on new input.

**Root cause:** No contract versioning or backward compatibility checks.

**Fix:**
1. Version contracts (e.g., `contract_version: "1.2"`)
2. Add backward compatibility: new fields are optional, old fields are deprecated but still present
3. Test contract changes with downstream skills before deploying

**Example:**
```
Contract v1.0: {"author_name": "string", "author_id": "string"}
Contract v1.1: {"author_name": "string", "author_id": "string", "follower_count": "number (optional)"}
Contract v2.0: {"name": "string", "id": "string", "followers": "number"}  ← Breaking change!

Migration path:
  v1.0 → v1.1: Add optional field (backward compatible)
  v1.1 → v2.0: Rename fields (breaking) → provide adapter skill that converts v2.0 → v1.1
```

## Pitfall 8: Missing Idempotency

**Symptom:** Workflow fails at step 3, restarts from step 1. Step 1 sends email notification again. User gets 3 emails.

**Root cause:** Step 1 is not idempotent (sending email is a side effect that can't be undone).

**Fix:**
1. Identify non-idempotent steps (email, SMS, payment, DB insert without dedup)
2. Add idempotency keys or conditional execution
3. Check if step already completed before running it

**Example:**
```python
def send_email_with_idempotency(to, subject, body, run_id, step_name):
    idempotency_key = f"{run_id}_{step_name}"
    
    # Check if already sent
    if email_already_sent(idempotency_key):
        return {"status": "skipped", "reason": "already_sent"}
    
    # Send email with idempotency key
    response = email_api.send(to, subject, body, idempotency_key=idempotency_key)
    
    # Record that we sent it
    record_email_sent(idempotency_key)
    
    return response
```

## Pitfall 9: Over-Parallelization

**Symptom:** Workflow spawns 1000 parallel tasks. System runs out of memory, API rate limits hit, debugging impossible.

**Root cause:** "Parallel is faster" assumption without considering resource limits.

**Fix:**
1. Set max concurrency (e.g., 10 parallel tasks at a time)
2. Use semaphore or queue to limit concurrent execution
3. Monitor resource usage (CPU, memory, API calls)

**Example:**
```python
from concurrent.futures import ThreadPoolExecutor

# Limit to 10 concurrent tasks
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_item, item) for item in items]
    results = [f.result() for f in futures]
```

## Pitfall 10: Human-in-the-Loop Timeout

**Symptom:** Workflow waits for human approval. Human forgets. Workflow hangs forever.

**Root cause:** No timeout or escalation for human review points.

**Fix:**
1. Set timeout for human review (e.g., 24 hours)
2. Send reminder after 12 hours
3. After timeout, either:
   - Auto-approve with warning (if low risk)
   - Escalate to manager (if high risk)
   - Stop and notify (if critical)

**Example:**
```python
def wait_for_human_approval(run_id, timeout_hours=24):
    start_time = time.time()
    reminder_sent = False
    
    while True:
        status = check_approval_status(run_id)
        
        if status == "approved":
            return {"status": "approved"}
        elif status == "rejected":
            return {"status": "rejected", "reason": status.reason}
        
        elapsed_hours = (time.time() - start_time) / 3600
        
        if elapsed_hours > timeout_hours:
            return {"status": "timeout", "action": "escalate_to_manager"}
        
        if elapsed_hours > timeout_hours / 2 and not reminder_sent:
            send_reminder(run_id)
            reminder_sent = True
        
        time.sleep(300)  # Check every 5 minutes
```

## Pitfall 11: Missing Observability

**Symptom:** Workflow fails in production. No logs, no metrics, no way to debug.

**Root cause:** Logging and monitoring not designed upfront.

**Fix:**
1. Log every step start/end with `run_id`, `step_name`, `timestamp`
2. Log every API call with request/response (redact secrets)
3. Track metrics: success rate, latency, cost per run
4. Set up alerts for failure rate > 5% or latency > 2x baseline

**Example:**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_skill_with_logging(skill_name, input_data, run_id):
    logger.info(f"Starting {skill_name}", extra={
        "run_id": run_id,
        "skill_name": skill_name,
        "input_size": len(json.dumps(input_data))
    })
    
    start_time = time.time()
    
    try:
        output = run_skill(skill_name, input_data)
        duration = time.time() - start_time
        
        logger.info(f"Completed {skill_name}", extra={
            "run_id": run_id,
            "skill_name": skill_name,
            "duration_seconds": duration,
            "output_size": len(json.dumps(output))
        })
        
        return output
    except Exception as e:
        duration = time.time() - start_time
        
        logger.error(f"Failed {skill_name}", extra={
            "run_id": run_id,
            "skill_name": skill_name,
            "duration_seconds": duration,
            "error": str(e)
        })
        
        raise
```

## Pitfall 12: Platform-Specific Logic in Reusable Skills

**Symptom:** `image-ocr` skill works for Douyin but fails for Xiaohongshu. Turns out it had Douyin-specific URL parsing inside.

**Root cause:** "Quick fix" added platform logic to reusable skill. Over time, reusable skill accumulated platform-specific code.

**Fix:**
1. Extract platform-specific logic into platform-specific skills
2. Reusable skill only handles generic logic
3. Orchestrator routes to platform-specific skill first, then reusable skill

**Example:**
```
Bad:
  image-ocr skill:
    1. Parse Douyin URL to extract image ID
    2. Download image
    3. Run OCR

Good:
  parse-douyin-image-url skill:
    1. Parse Douyin URL to extract image ID
  
  image-ocr skill:
    1. Download image from URL
    2. Run OCR
  
  Orchestrator:
    1. parse-douyin-image-url → image_url
    2. image-ocr(image_url) → text
```

## Pitfall 13: No Cost Monitoring

**Symptom:** Workflow runs successfully, but costs $50 per run instead of expected $5. No one noticed until end of month.

**Root cause:** No cost tracking or budget alerts.

**Fix:**
1. Track cost per step (API calls, model inference, compute time)
2. Sum cost per `run_id`
3. Alert if cost > 2x expected
4. Provide cost breakdown in workflow output

**Example:**
```python
class CostTracker:
    def __init__(self, run_id):
        self.run_id = run_id
        self.costs = []
    
    def add_cost(self, step_name, cost, reason):
        self.costs.append({
            "step_name": step_name,
            "cost": cost,
            "reason": reason,
            "timestamp": time.time()
        })
    
    def total_cost(self):
        return sum(c["cost"] for c in self.costs)
    
    def report(self):
        return {
            "run_id": self.run_id,
            "total_cost": self.total_cost(),
            "breakdown": self.costs
        }

# Usage
tracker = CostTracker(run_id)
tracker.add_cost("audio-transcribe", 3.00, "30 videos × $0.10/min")
tracker.add_cost("llm-polish", 0.50, "50k tokens × $0.01/1k")

if tracker.total_cost() > budget:
    raise BudgetExceeded(f"Cost ${tracker.total_cost()} exceeds budget ${budget}")
```

## Pitfall 14: Inadequate Failure Modes

**Symptom:** Workflow fails with generic error: "Something went wrong." No way to know which step failed or why.

**Root cause:** Error handling catches all exceptions and returns generic message.

**Fix:**
1. Define specific failure modes for each step (timeout, empty output, invalid data, auth error)
2. Return structured error with step name, failure type, and diagnostic info
3. Orchestrator routes based on failure type

**Example:**
```python
# Bad
try:
    result = collect_works(author_id)
except Exception as e:
    return {"status": "error", "message": "Failed to collect works"}

# Good
try:
    result = collect_works(author_id)
except TimeoutError:
    return {
        "status": "failed",
        "step": "collect-works",
        "failure_type": "timeout",
        "diagnostic": {"author_id": author_id, "timeout_seconds": 30}
    }
except RateLimitError as e:
    return {
        "status": "failed",
        "step": "collect-works",
        "failure_type": "rate_limit",
        "diagnostic": {"retry_after": e.retry_after}
    }
except AuthError:
    return {
        "status": "failed",
        "step": "collect-works",
        "failure_type": "auth",
        "diagnostic": {"message": "API token expired"}
    }
```
