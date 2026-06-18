# Testing Procedures for Atomic + Orchestration Workflows

Step 8 in the main design workflow asks you to verify the architecture. This document provides actionable test procedures instead of a question checklist.

## Test 1: Single Responsibility Verification

**Goal:** Confirm each atomic skill does one coherent job.

**Procedure:**
1. List all actions performed by the skill (from its Process section)
2. For each action, ask: "Does this action contribute to the skill's stated responsibility?"
3. If any action doesn't contribute, it's a candidate for extraction

**Pass criteria:**
- All actions contribute to one responsibility
- Skill name is a verb-noun pair that describes the responsibility (e.g., `parse-author`, `image-ocr`)

**Fail signals:**
- Skill name contains "and" or "plus" (e.g., `parse-and-validate-author`)
- Process section has unrelated actions (e.g., "parse author, then send email notification")
- Output schema has fields unrelated to the stated responsibility

**Example:**
```
Skill: parse-author
Responsibility: Extract author metadata from platform profile
Actions:
  1. Fetch profile page ✓ (contributes)
  2. Parse HTML for author name ✓ (contributes)
  3. Extract follower count ✓ (contributes)
  4. Send webhook notification ✗ (doesn't contribute — extract to notify-webhook skill)
```

## Test 2: Independent Testability

**Goal:** Confirm each atomic skill can be tested without running the full workflow.

**Procedure:**
1. Identify the skill's input contract (required fields, formats)
2. Create a minimal test input (mock data or real sample)
3. Run the skill in isolation (no orchestrator, no other skills)
4. Verify output matches contract

**Pass criteria:**
- Skill runs without errors
- Output schema matches contract
- Failure behavior matches contract (if input invalid, returns documented error)

**Fail signals:**
- Skill requires another skill to be called first (dependency not declared)
- Skill reads from hardcoded file path or environment variable not in contract
- Skill calls another skill internally (hidden dependency)

**Example test harness:**
```bash
# Test parse-author in isolation
INPUT='{"url": "https://douyin.com/user/12345"}'
EXPECTED_OUTPUT_SCHEMA='{"author_name": "string", "author_id": "string", "follower_count": "number"}'

# Run skill
OUTPUT=$(run_skill parse-author "$INPUT")

# Validate schema
echo "$OUTPUT" | jq -e '.author_name and .author_id and .follower_count'
```

## Test 3: Contract Validation

**Goal:** Confirm all handoffs are explicit and stable.

**Procedure:**
1. For each orchestration step, check:
   - Input source is explicitly named (not "previous output" — which previous output?)
   - Output schema is documented
   - Failure behavior is documented
2. For each atomic skill, check:
   - Input contract lists required and optional fields
   - Output contract lists all fields and their types
   - Preconditions are listed (tools, credentials, files)

**Pass criteria:**
- No implicit handoffs (every input source is explicit)
- All contracts have input, output, and failure sections
- Contracts are structured (JSON schema or table), not prose-only

**Fail signals:**
- Orchestration step says "input from previous step" without naming the step
- Atomic skill says "returns a result object" without listing fields
- Contract uses vague terms like "appropriate data" or "relevant information"

**Example:**
```
Step 2: collect-works
  Input source: step_1.author_id ✗ (unclear — step 1 is parse-author, but which field?)
  Output: "list of works" ✗ (vague — what fields?)

Corrected:
Step 2: collect-works
  Input source: step_1_parse_author.author_id
  Input contract: {"author_id": "string (required)", "count": "number (optional, default 100)"}
  Output contract: [{"work_id": "string", "type": "image|video", "url": "string", "created_at": "ISO8601"}]
  Failure: {"status": "error", "message": "string", "partial_results": []}
```

## Test 4: Failure Route Verification

**Goal:** Confirm every failure-prone step has a fallback or intentional stop.

**Procedure:**
1. Identify failure-prone steps (network calls, API requests, model inference, file I/O)
2. For each, check:
   - Failure signal is defined (timeout, empty output, invalid data)
   - First response is defined (retry, alternate route)
   - Final fallback is defined (partial result, manual review, stop)
3. Simulate each failure and verify the orchestrator routes correctly

**Pass criteria:**
- Every failure-prone step has a fallback table entry
- Fallback routes are testable (can simulate failure and verify routing)
- No step has "ignore error and continue" as the only fallback

**Fail signals:**
- Network call has no timeout
- API call has no retry logic
- Model inference has no fallback for empty output
- Orchestrator says "if error, stop" without specifying what to do with partial results

**Example test:**
```bash
# Simulate API timeout
MOCK_API_DELAY=60s  # Force timeout
OUTPUT=$(run_skill collect-works '{"author_id": "12345", "count": 10}')

# Verify fallback triggered
echo "$OUTPUT" | jq -e '.status == "partial" and .failed_items | length > 0'
```

## Test 5: Platform Isolation

**Goal:** Confirm platform-specific skills are isolated from reusable capabilities.

**Procedure:**
1. List all atomic skills
2. Classify each: reusable, domain-specific, platform-specific, workflow-specific
3. Check that platform-specific skills don't contain reusable logic
4. Check that reusable skills don't contain platform-specific logic

**Pass criteria:**
- Platform-specific skills only handle platform API/format quirks
- Reusable skills work across platforms (tested with 2+ platform inputs)
- No skill is both platform-specific and reusable

**Fail signals:**
- `image-ocr` skill contains Douyin-specific URL parsing
- `parse-author` skill contains generic OCR logic
- Swapping platforms requires editing reusable skills

**Example:**
```
Skill: image-ocr (should be reusable)
  Process:
    1. Download image from URL ✓ (generic)
    2. Run OCR model ✓ (generic)
    3. Parse Douyin-specific JSON response ✗ (platform-specific — extract to parse-douyin-response)
```

## Test 6: Resume Safety

**Goal:** Confirm the workflow can resume safely after interruption.

**Procedure:**
1. Run the workflow until it checkpoints
2. Kill the process (simulate crash)
3. Restart the workflow with same `run_id`
4. Verify:
   - Completed steps are skipped
   - Failed/partial steps are retried
   - No duplicate side effects (emails, DB inserts, API calls)

**Pass criteria:**
- Workflow resumes from checkpoint, not from beginning
- Idempotent steps don't duplicate work
- Non-idempotent steps are wrapped in idempotency keys or conditional writes

**Fail signals:**
- Workflow restarts from beginning (no checkpoint loaded)
- Email sent twice (non-idempotent step retried without guard)
- DB has duplicate rows (append-only step retried without dedup)

**Example test:**
```bash
# Run workflow until step 3
RUN_ID=$(start_workflow)
wait_for_checkpoint "$RUN_ID" "step_3"

# Kill process
kill_workflow "$RUN_ID"

# Resume
RESUME_OUTPUT=$(resume_workflow "$RUN_ID")

# Verify step 1 and 2 skipped
echo "$RESUME_OUTPUT" | grep -q "step_1: skipped (already completed)"
echo "$RESUME_OUTPUT" | grep -q "step_2: skipped (already completed)"
echo "$RESUME_OUTPUT" | grep -q "step_3: retrying from checkpoint"
```

## Test 7: Human Decision Points

**Goal:** Confirm human decisions are explicitly marked and can't be auto-approved.

**Procedure:**
1. Identify all human review points in the orchestration flow
2. For each, check:
   - Marked as `STOP: wait for user confirmation`
   - Input to human is clear (what are they reviewing?)
   - Output from human is clear (what decision are they making?)
   - No automatic timeout that approves silently

**Pass criteria:**
- All human decisions are marked with STOP
- Human input/output is documented
- No auto-approval timeout unless explicitly requested by user

**Fail signals:**
- Orchestrator says "if user doesn't respond in 5 minutes, auto-approve"
- Human review point doesn't specify what's being reviewed
- Workflow proceeds without waiting for human input

## Test 8: Cost and Time Estimation

**Goal:** Confirm the workflow has realistic cost and time estimates.

**Procedure:**
1. For each step, estimate:
   - API calls (count × cost per call)
   - Model inference (tokens × cost per token)
   - Wall time (expected duration)
2. Sum across all steps
3. Check if total is within user's budget (if specified)

**Pass criteria:**
- Cost estimate is documented
- Time estimate is documented
- If budget is tight, cheaper alternatives are identified

**Fail signals:**
- No cost estimate
- Estimate is wildly off (actual cost 10x higher than estimate)
- No fallback for budget exceeded

**Example:**
```
Workflow: Douyin author data collection (50 works)
  Step 1 (parse-author): 1 API call, 2s, $0.00
  Step 2 (collect-works): 5 API calls, 30s, $0.00
  Step 3a (image-ocr, 20 images): 20 API calls, 60s, $0.20
  Step 3b (audio-transcribe, 30 videos): 30 GPU-minutes, 90s, $3.00
  Step 4 (llm-polish): 50k tokens, 10s, $0.50
  Total: ~3 minutes, ~$3.70
```

## Automated Test Harness

For workflows with structured contracts, build an automated test harness:

```python
# test_workflow.py
import json
import subprocess

def test_atomic_skill(skill_name, test_input, expected_output_schema):
    """Test an atomic skill in isolation."""
    result = subprocess.run(
        ["run_skill", skill_name, json.dumps(test_input)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Skill failed: {result.stderr}"
    
    output = json.loads(result.stdout)
    assert validate_schema(output, expected_output_schema), \
        f"Output doesn't match schema: {output}"
    
    return output

def test_orchestration_step(step_name, input_data, expected_output_schema):
    """Test an orchestration step with mocked atomic skills."""
    # Mock atomic skill outputs
    # Run orchestration step
    # Verify output matches schema
    # Verify correct skills were called
    pass

# Run tests
test_atomic_skill(
    "parse-author",
    {"url": "https://douyin.com/user/12345"},
    {"author_name": "string", "author_id": "string"}
)
```
