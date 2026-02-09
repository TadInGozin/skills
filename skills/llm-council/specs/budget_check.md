# Stage 0.3: Resource Budget Check

> Chairman performs this check at initialization and before each stage transition.
> **Source of Truth**: `protocols/standard.yaml` → `resource_budget`

## When to Check

1. **Initialization** (after Stage 0.2): Set start_time, total_budget based on selected mode
2. **Before Stage 0.5**: Check elapsed time
3. **Before Stage 2**: Check elapsed time — may degrade Deep → Standard
4. **Before each debate round** (Deep only): Check remaining time
5. **Before Stage 3**: Final check

## Decision Logic

```
elapsed = now - start_time
ratio = elapsed / total_budget

if strict_mode:
    if ratio >= 1.0 → STOP (hard failure)
    else → CONTINUE

if ratio >= trigger_ratio (default 0.8):
    if current_mode == "deep" → DEGRADE to "standard"
    elif current_mode == "standard" → DEGRADE to "quick"
    elif current_mode == "quick" → STOP

if ratio < trigger_ratio → CONTINUE
```

## Degradation Data Reuse

When degrading, reuse completed work:
- **Deep → Standard**: Use Stage 1 responses. Skip remaining debate rounds. Run Stage 2S (cross-eval) if time permits, else degrade further.
- **Standard → Quick**: Use Stage 1 responses. Skip Stage 2. Go directly to Stage 3 (Quick synthesis).
- **Participant overflow**: If discovered LLMs > `max_participants`, keep top N by detection score.

## Output Format

```json
{
  "action": "continue|degrade|stop",
  "reason": "<why this action>",
  "elapsed_seconds": 45,
  "budget_seconds": 180,
  "ratio": 0.25,
  "degrade_to": "standard|quick|null",
  "adjusted_limits": {}
}
```

## Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `start_time` | timestamp | When the council started | Yes |
| `total_budget` | number | Total seconds for selected mode | Yes |
| `current_mode` | string | Current protocol mode | Yes |
| `elapsed` | number | Seconds elapsed so far | Yes |
| `strict` | boolean | Whether strict mode is enabled | Yes |
| `trigger_ratio` | number | Degradation trigger (default 0.8) | Yes |
