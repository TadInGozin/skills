# Stage 2: Blind Peer Evaluation

## Prompt Template

Use this template when evaluating responses. **Remember: This is blind evaluation.**

---

Please evaluate the following responses to a question.

## Question

{{question}}

## Responses to Evaluate

{{#each responses}}
### Response {{label}}

{{content}}

---
{{/each}}

## Evaluation Rubric

Score each response on these dimensions (1-10 scale):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Accuracy | {{rubric.accuracy.weight}} | Correctness and reliability of information |
| Verifiability | {{rubric.verifiability.weight}} | Evidence and verifiable steps provided |
| Completeness | {{rubric.completeness.weight}} | Coverage of all relevant aspects |
| Clarity | {{rubric.clarity.weight}} | Clear and understandable expression |
| Actionability | {{rubric.actionability.weight}} | Specific, executable recommendations |
| Relevance | {{rubric.relevance.weight}} | Addresses the core of the question |

## Disqualification Rules

Check for these issues:
- **Critical Factual Error**: Cap score at 5
- **Fabricated References**: Disqualify
- **Safety/Privacy Violation**: Disqualify

## Output Format

Provide evaluation in structured format:

```json
{
  "evaluations": [
    {
      "response_label": "Response A",
      "scores": {
        "accuracy": <score>,
        "verifiability": <score>,
        "completeness": <score>,
        "clarity": <score>,
        "actionability": <score>,
        "relevance": <score>
      },
      "rationale": {
        "accuracy": "<brief explanation>",
        "verifiability": "<brief explanation>",
        "completeness": "<brief explanation>",
        "clarity": "<brief explanation>",
        "actionability": "<brief explanation>",
        "relevance": "<brief explanation>"
      },
      "disqualified": false,
      "disqualification_reason": null
    }
  ],
  "disagreements": [
    {
      "topic": "<what the disagreement is about>",
      "positions": {
        "Response A": "<position>",
        "Response B": "<position>"
      },
      "verified": false,
      "resolution": null
    }
  ]
}
```

---

## Variables

| Variable | Description |
|----------|-------------|
| `question` | The original question |
| `responses` | Array of {label, content} |
| `rubric` | Dimension weights |

## Notes for Execution

1. **Blind Evaluation**: Do not try to identify which response is yours
2. Be objective and fair to all responses
3. Provide specific rationale citing response content
4. Identify any factual disagreements between responses
