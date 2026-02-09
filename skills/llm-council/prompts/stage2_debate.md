# Stage 2D: Debate Loop (Deep Mode)

> Multi-round structured debate with moderator-assessed convergence.
> **Applies to**: Deep mode only (v4.8.1).

## Execution Flow

```
1. Anonymize: Shuffle responses, assign Debater A/B/C...
2. Round 1: Each debater reviews ALL other responses and argues their position
3. Moderator assesses: Should the debate continue?
4. Round 2-N: Debaters see previous round's arguments, may revise position
5. Exit: When convergence is reached OR max_rounds exhausted
6. Output: Final stances + debate_log → Stage 3 (Deep synthesis)
```

### Convergence Conditions (exit when ANY is true)

- `agreement_score >= 0.8` AND `new_points_ratio <= 0.15`
- All debaters chose `revision: "no_change"` in the round
- `round >= max_rounds` (default: 3)

### Constraints

- `min_rounds`: 2 (ensure at least one rebuttal)
- `max_rounds`: 3 (prevent infinite loops)
- Timeout per round: inherits from `execution.timeout.per_llm_call`

---

## Debater Prompt Template

```handlebars
You are a debater in a structured deliberation. Your position is based on your original response.

## Question
{{question}}

## Your Original Response
{{own_response}}

## Other Debaters' Responses
{{#each other_responses}}
### Debater {{label}}
{{{content}}}
---
{{/each}}

{{#if previous_round}}
## Previous Round Arguments
{{#each previous_round}}
### Debater {{label}}
{{{argument}}}
---
{{/each}}
{{/if}}

## Instructions

Analyze the other positions and respond with structured JSON:

```json
{
  "stance": "maintain|concede|partial_concede",
  "key_points": ["<your strongest arguments>"],
  "counterpoints": [
    {"target": "Debater X", "point": "<what they got wrong>", "evidence": "<why>"}
  ],
  "revision": "no_change|minor_update|major_revision",
  "revised_position": "<your updated answer if revision != no_change>",
  "confidence": 0.0-1.0
}
```
```

## Debater Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | Original question | Yes |
| `own_response` | string | This debater's Stage 1 response | Yes |
| `other_responses` | array | Other debaters' responses `{label, content}` | Yes |
| `previous_round` | array | Previous round arguments `{label, argument}` | No (null for round 1) |

---

## Moderator Prompt Template

```handlebars
You are the debate moderator. Assess whether the debate has reached convergence.

## Question
{{question}}

## Current Round: {{round_number}} of {{max_rounds}}

## This Round's Arguments
{{#each arguments}}
### Debater {{label}}
- Stance: {{stance}}
- Confidence: {{confidence}}
- Revision: {{revision}}
{{#each key_points}}- {{this}}
{{/each}}
---
{{/each}}

## Assessment Instructions

Evaluate convergence and respond with structured JSON:

```json
{
  "should_stop": true|false,
  "agreement_score": 0.0-1.0,
  "new_points_ratio": 0.0-1.0,
  "consensus_answer": "<emerging consensus if agreement_score > 0.6, else null>",
  "remaining_disagreements": ["<unresolved points>"],
  "next_round_focus": "<what debaters should address if continuing, else null>"
}
```
```

## Moderator Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | Original question | Yes |
| `round_number` | number | Current round (1-based) | Yes |
| `max_rounds` | number | Maximum rounds allowed | Yes |
| `arguments` | array | This round's debater outputs | Yes |

---

## Output to Stage 3

The debate loop passes the following to Stage 3 (Deep synthesis):

```json
{
  "mode": "deep",
  "rounds_completed": 2,
  "final_stances": [
    {"debater": "A", "stance": "maintain", "confidence": 0.9, "revised_position": "..."},
    {"debater": "B", "stance": "partial_concede", "confidence": 0.7, "revised_position": "..."}
  ],
  "convergence_status": {
    "agreement_score": 0.85,
    "new_points_ratio": 0.1,
    "consensus_answer": "...",
    "remaining_disagreements": []
  },
  "debate_log": ["<round 1 summary>", "<round 2 summary>"]
}
```
