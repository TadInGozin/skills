# Step 0.2: Protocol Mode Selection

> Selects Quick, Standard, or Deep mode based on question analysis.
> **Source of Truth**: `protocols/standard.yaml` → `protocol_modes`

## Template

```handlebars
Select the appropriate protocol mode for this question.

## Question

{{question}}

{{#if context}}
## Context

{{context}}
{{/if}}

## Available Modes

| Mode | When to Use |
|------|-------------|
| **quick** | Simple, subjective, or low-stakes questions. Keywords: quick, simple, brief, opinion, preference, poll, name, list |
| **standard** | Technical, multi-faceted, or moderate-stakes questions. Keywords: compare, recommend, explain, analyze, review, decide, evaluate |
| **deep** | High-stakes, complex, controversial, or safety-critical questions. Keywords: debate, deep, thorough, critical, audit, risk, security, architecture |

## Selection Rules

1. If the user explicitly requests a mode (e.g., "use deep mode"), use that mode.
2. Otherwise, analyze the question against the keywords and signals above.
3. Default to **standard** if uncertain.

## Output Format

```json
{
  "selected_mode": "quick|standard|deep",
  "reason": "<one-sentence justification>",
  "override": false,
  "signals_detected": ["<matching keywords or signals>"]
}
```
```

## Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | The user's question | Yes |
| `context` | string | Additional context | No |
