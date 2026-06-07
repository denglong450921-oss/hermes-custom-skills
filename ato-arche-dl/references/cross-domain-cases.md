# Cross-Domain Case Studies

Real-world applications of the atomic + orchestration pattern beyond content collection.

## Case 1: Customer Onboarding Workflow

**Domain:** SaaS platform  
**Goal:** Automate new customer setup: account creation, data import, training, activation check.

### Atomic Skills

| Skill | Responsibility | Classification | Reuse |
|-------|---------------|----------------|-------|
| `create-account` | Create user account in auth system | Platform-specific | No |
| `import-data` | Import customer's existing data from CSV/API | Reusable | Yes |
| `validate-data` | Check imported data for completeness/validity | Domain-specific | Yes |
| `send-welcome-email` | Send onboarding email with next steps | Reusable | Yes |
| `schedule-training` | Book training session on calendar | Platform-specific | No |
| `check-activation` | Verify customer completed key actions (login, invite team, configure settings) | Workflow-specific | No |

### Orchestration Flow

```
Step 0: create-account
  Input: {email, name, company}
  Output: {user_id, temp_password}
  Route: Step 1

Step 1: import-data
  Input: {user_id, data_source_url}
  Output: {import_status, record_count}
  Route: If import_status == "success" → Step 2, else → Step 1b (manual import guide)

Step 1b: send-manual-import-guide
  Input: {user_id, email}
  Output: {email_sent}
  Route: Step 2

Step 2: validate-data
  Input: {user_id}
  Output: {validation_status, missing_fields[]}
  Route: If validation_status == "complete" → Step 3, else → Step 2b (request missing data)

Step 2b: request-missing-data
  Input: {user_id, missing_fields[]}
  Output: {request_sent}
  Route: STOP (wait for user to provide data)

Step 3: send-welcome-email
  Input: {user_id, email}
  Output: {email_sent}
  Route: Step 4

Step 4: schedule-training
  Input: {user_id, email}
  Output: {training_scheduled, training_date}
  Route: Step 5

Step 5: check-activation (after 7 days)
  Input: {user_id}
  Output: {activation_status, completed_actions[]}
  Route: If activation_status == "complete" → Done, else → Step 5b (nudge)

Step 5b: send-nudge-email
  Input: {user_id, incomplete_actions[]}
  Output: {email_sent}
  Route: Done (manual follow-up by CSM if still inactive after 14 days)
```

### Key Design Decisions

1. **Human review at Step 2b:** Missing data requires user input, can't auto-generate.
2. **Delayed Step 5:** Activation check runs 7 days after onboarding, not immediately.
3. **Partial success handling:** If data import fails (Step 1), workflow continues with manual guide (Step 1b) instead of stopping.
4. **Reuse:** `import-data`, `validate-data`, `send-welcome-email` used in other workflows (partner onboarding, internal employee setup).

### Pitfall Avoided

**Initial design:** `import-data` skill contained CSV parsing and API integration for Salesforce, HubSpot, and custom APIs.  
**Problem:** 800 lines, hard to test, adding new platform required editing the skill.  
**Fix:** Split into `import-csv` (reusable), `import-salesforce` (platform-specific), `import-hubspot` (platform-specific). Orchestrator routes based on `data_source_type`.

## Case 2: ML Model Training Pipeline

**Domain:** Machine learning  
**Goal:** Train model on new data: preprocess, train, evaluate, deploy if quality threshold met.

### Atomic Skills

| Skill | Responsibility | Classification | Reuse |
|-------|---------------|----------------|-------|
| `fetch-data` | Pull training data from data warehouse | Platform-specific | No |
| `preprocess-data` | Clean, normalize, split train/test | Domain-specific | Yes |
| `train-model` | Run training loop with hyperparameters | Workflow-specific | No |
| `evaluate-model` | Calculate metrics (accuracy, precision, recall) | Reusable | Yes |
| `compare-baseline` | Compare new model vs current production model | Workflow-specific | No |
| `deploy-model` | Deploy to production endpoint | Platform-specific | No |
| `notify-stakeholders` | Send Slack message with results | Reusable | Yes |

### Orchestration Flow

```
Step 0: fetch-data
  Input: {dataset_id, date_range}
  Output: {data_path, record_count}
  Checkpoint: true (data fetch is expensive)
  Route: Step 1

Step 1: preprocess-data
  Input: {data_path}
  Output: {train_path, test_path, preprocessing_stats}
  Checkpoint: true
  Route: Step 2

Step 2: train-model
  Input: {train_path, hyperparameters}
  Output: {model_path, training_metrics}
  Budget: {max_gpu_hours: 10, on_exceeded: "stop_and_report"}
  Checkpoint: true
  Route: Step 3

Step 3: evaluate-model
  Input: {model_path, test_path}
  Output: {metrics: {accuracy, precision, recall, f1}}
  Route: Step 4

Step 4: compare-baseline
  Input: {metrics, baseline_metrics}
  Output: {comparison: {improvement, regression, significant_changes[]}}
  Route: If improvement > 5% → Step 5, else → Step 6 (notify no improvement)

Step 5: deploy-model
  Input: {model_path, endpoint_name}
  Output: {deployment_status, endpoint_url}
  Route: STOP: wait for human approval before traffic switch
  (After approval) → Step 7

Step 6: notify-no-improvement
  Input: {metrics, baseline_metrics}
  Output: {notification_sent}
  Route: Done

Step 7: notify-stakeholders
  Input: {model_name, metrics, endpoint_url}
  Output: {notification_sent}
  Route: Done
```

### Key Design Decisions

1. **Budget constraint at Step 2:** Training can run away (infinite epochs), so max GPU hours enforced.
2. **Checkpoint after expensive steps:** Data fetch (Step 0), preprocessing (Step 1), training (Step 2) all checkpointed.
3. **Human approval at Step 5:** Deployment to production requires human sign-off, can't auto-deploy.
4. **Conditional routing:** Step 4 compares against baseline, only deploys if significant improvement.
5. **Parallel potential:** If training multiple model variants, Step 2 can fan out (train-model-A, train-model-B, train-model-C) then fan in at Step 3 (evaluate all, pick best).

### Reuse Analysis

| Skill | Reused in | Notes |
|-------|-----------|-------|
| `preprocess-data` | Data analysis workflows, A/B test analysis | Same cleaning logic |
| `evaluate-model` | Model monitoring (daily eval of production model) | Same metrics |
| `notify-stakeholders` | Alert on model drift, alert on data quality issues | Same Slack integration |

## Case 3: E-commerce Order Fulfillment

**Domain:** E-commerce  
**Goal:** Process order: payment, inventory check, warehouse pick/pack, shipping, tracking.

### Atomic Skills

| Skill | Responsibility | Classification | Reuse |
|-------|---------------|----------------|-------|
| `process-payment` | Charge customer's payment method | Platform-specific | No |
| `check-inventory` | Verify items in stock at nearest warehouse | Domain-specific | Yes |
| `reserve-inventory` | Temporarily reserve items for order | Domain-specific | Yes |
| `send-to-warehouse` | Send pick/pack instructions to warehouse system | Platform-specific | No |
| `track-shipment` | Get tracking number and status from carrier | Platform-specific | No |
| `send-confirmation-email` | Notify customer of order status | Reusable | Yes |
| `handle-refund` | Refund payment if order can't be fulfilled | Workflow-specific | No |

### Orchestration Flow

```
Step 0: process-payment
  Input: {order_id, payment_method, amount}
  Output: {payment_status, transaction_id}
  Idempotency key: {order_id}
  Route: If payment_status == "success" → Step 1, else → Step 0b (payment failed)

Step 0b: send-payment-failed-email
  Input: {order_id, customer_email, failure_reason}
  Output: {email_sent}
  Route: Done (order cancelled)

Step 1: check-inventory
  Input: {order_id, items[], customer_location}
  Output: {availability: {in_stock_items[], out_of_stock_items[]}}
  Route: If all in stock → Step 2, else → Step 1b (partial availability)

Step 1b: handle-partial-availability
  Input: {order_id, in_stock_items[], out_of_stock_items[]}
  Output: {customer_choice: "ship_partial" | "wait" | "cancel"}
  Route: STOP: wait for customer decision
  (If "ship_partial") → Step 2 with in_stock_items only
  (If "wait") → Schedule retry in 3 days
  (If "cancel") → Step 6 (refund)

Step 2: reserve-inventory
  Input: {order_id, items[]}
  Output: {reservation_id, expires_at}
  Idempotency key: {order_id}
  Route: Step 3

Step 3: send-to-warehouse
  Input: {order_id, items[], shipping_address, reservation_id}
  Output: {warehouse_order_id, estimated_ship_date}
  Route: Step 4

Step 4: track-shipment
  Input: {warehouse_order_id}
  Output: {tracking_number, carrier, estimated_delivery}
  Route: Step 5

Step 5: send-confirmation-email
  Input: {order_id, customer_email, tracking_number, estimated_delivery}
  Output: {email_sent}
  Route: Done

Step 6: handle-refund
  Input: {order_id, transaction_id, reason}
  Output: {refund_status, refund_id}
  Route: Step 6b (refund confirmation email)

Step 6b: send-refund-confirmation-email
  Input: {order_id, customer_email, refund_id}
  Output: {email_sent}
  Route: Done
```

### Key Design Decisions

1. **Idempotency at Steps 0 and 2:** Payment and inventory reservation must not duplicate on retry.
2. **Human decision at Step 1b:** Customer chooses how to handle out-of-stock items.
3. **Failure route at Step 6:** If order can't be fulfilled, refund payment and notify customer.
4. **Parallel potential:** Step 1 (check inventory) could fan out to check multiple warehouses in parallel, then pick the one with best availability.

### Pitfall Encountered

**Initial design:** `reserve-inventory` skill didn't have expiration. Reserved items stayed reserved forever if order failed later.  
**Problem:** Inventory appeared "in stock" but was actually reserved, blocking other orders.  
**Fix:** Added `expires_at` field to reservation. Warehouse system auto-releases expired reservations.

## Case 4: Content Moderation Pipeline

**Domain:** Social media platform  
**Goal:** Review user-generated content: automated filtering, human review for edge cases, action (approve/reject/flag).

### Atomic Skills

| Skill | Responsibility | Classification | Reuse |
|-------|---------------|----------------|-------|
| `extract-content` | Pull text, images, video from post | Platform-specific | No |
| `automated-text-filter` | Check text against banned words, spam patterns | Domain-specific | Yes |
| `automated-image-filter` | Run image through NSFW detection model | Reusable | Yes |
| `score-risk` | Combine automated signals into risk score (0-100) | Workflow-specific | No |
| `queue-for-human-review` | Add to moderator queue if risk score in gray zone | Workflow-specific | No |
| `human-review` | Moderator reviews content and decides | Workflow-specific | No |
| `apply-action` | Approve, reject, or flag content based on decision | Platform-specific | No |
| `notify-user` | Send notification to user about action taken | Reusable | Yes |

### Orchestration Flow

```
Step 0: extract-content
  Input: {post_id}
  Output: {text, images[], video_url}
  Route: Step 1 (parallel)

Step 1a: automated-text-filter
  Input: {text}
  Output: {text_risk_score, matched_patterns[]}
  Route: Step 2

Step 1b: automated-image-filter
  Input: {images[]}
  Output: {image_risk_scores[], flagged_images[]}
  Route: Step 2

Step 2: score-risk
  Input: {text_risk_score, image_risk_scores[]}
  Output: {overall_risk_score, risk_breakdown}
  Route: 
    If score < 20 → Step 3a (auto-approve)
    If score 20-80 → Step 3b (human review)
    If score > 80 → Step 3c (auto-reject)

Step 3a: apply-action (approve)
  Input: {post_id, action: "approve", reason: "low_risk"}
  Output: {action_applied}
  Route: Done (no notification needed for approval)

Step 3b: queue-for-human-review
  Input: {post_id, risk_score, flagged_content[]}
  Output: {queue_position, estimated_wait_time}
  Route: STOP: wait for human review

Step 3b-continued: human-review
  Input: {post_id, content, risk_breakdown}
  Output: {decision: "approve" | "reject" | "flag", moderator_notes}
  Route: Step 4

Step 3c: apply-action (reject)
  Input: {post_id, action: "reject", reason: "high_risk", risk_breakdown}
  Output: {action_applied}
  Route: Step 5

Step 4: apply-action (based on human decision)
  Input: {post_id, action: human_decision, reason: moderator_notes}
  Output: {action_applied}
  Route: Step 5

Step 5: notify-user
  Input: {user_id, post_id, action, reason}
  Output: {notification_sent}
  Route: Done
```

### Key Design Decisions

1. **Parallel execution at Step 1:** Text and image filters run in parallel, then combine scores.
2. **Three-tier routing at Step 2:** Low risk auto-approves, high risk auto-rejects, gray zone goes to human.
3. **No notification for approval:** Only notify users when content is rejected or flagged (avoid notification fatigue).
4. **Human review is blocking:** Step 3b waits for moderator, no auto-approval timeout (safety-critical).

### Reuse Analysis

| Skill | Reused in | Notes |
|-------|-----------|-------|
| `automated-image-filter` | Profile picture moderation, direct message image filtering | Same NSFW model |
| `notify-user` | Account warnings, feature announcements, password reset | Same notification system |

## Lessons Across Domains

1. **Human decisions are unavoidable in high-stakes workflows:** Deployment (ML), refunds (e-commerce), content moderation. Design explicit STOP points.

2. **Parallel execution saves time but adds complexity:** Fan-out/fan-in works for independent tasks (OCR multiple images, check multiple warehouses). Don't parallelize dependent steps.

3. **Idempotency is critical for side effects:** Payments, emails, DB writes. Use idempotency keys or conditional execution.

4. **Budget constraints prevent runaway costs:** ML training (GPU hours), API calls (rate limits), data processing (token limits).

5. **Partial success is better than total failure:** If 90% of items succeed, return partial result with failure details. Don't discard useful work.

6. **Platform-specific skills are inevitable:** Auth systems, payment processors, warehouse APIs. Isolate them so reusable skills stay clean.

7. **Checkpoints save money and time:** Expensive steps (data fetch, model training, video processing) should checkpoint so resume doesn't repeat work.
