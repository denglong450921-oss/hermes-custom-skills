# get_selection() Truncation Guide

Large frames produce `get_selection()` responses that exceed the 200K-char tool limit and get silently truncated. The `type` field becomes invisible, halting Step 0 routing.

## Symptoms

```
[Truncated: tool response was 202,672 chars. Full output could not be saved to sandbox.]
```

## Fallback flow

1. **Identify the frame** from whatever is visible at the end of the truncated output (look for `"id":"693:XXXX"` and `"name":"..."`).

2. **Get the selection type** via `get_design_context(depth=1)`. This returns a compact tree with types clearly labelled. The selected node is the first element in `context[0]`.

3. **If it's a FRAME**, go straight to `scan_text_nodes(frameId)` to get all text nodes in one clean call.

4. **Confirm your target** via `get_metadata()` which returns the file name and current page — helps disambiguate when working on a multi-page file.

## Example

```
# get_selection truncated — frame "7" suspected
get_design_context(depth=1)
# → confirms context[0].type = "FRAME", name = "7"

scan_text_nodes(nodeId="693:2205")
# → clean list of text nodes
```
