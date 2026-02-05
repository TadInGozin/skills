# Stage 0.5: Smart Rubric Selection & Weight Adjustment

> **Advanced Customization**: This template can be modified for custom selection logic.
> Default behavior is defined in SKILL.md.

## Prompt Template

```
## Task: Rubric Selection & Weight Adjustment

Analyze the user's question and determine the best evaluation rubric with appropriate weight adjustments.

### User Question

{{question}}

{{#if context}}
### Additional Context

{{context}}
{{/if}}

### Available Rubrics

| ID | Name | Focus |
|----|------|-------|
| code-review | Code Review | Security, code quality, fixes |
| factual-qa | Factual Q&A | Accuracy, verification |
| technical-decision | Technical Decision | Trade-offs, architecture |
| debugging | Debugging | Error diagnosis, solutions |
| summarization | Summarization | Faithfulness, key points |
| creative-writing | Creative Writing | Creativity, engagement |
| brainstorming | Brainstorming | Idea diversity, novelty |
| translation | Translation | Semantic accuracy, fluency |
| instructional | Instructional | Step-by-step clarity |
| information-extraction | Information Extraction | Schema compliance |
| project-planning | Project Planning | Feasibility, milestones |
| customer-support | Customer Support | Empathy, resolution |
| safety-critical | Safety Critical | Safety awareness, disclaimers |
| default | Default | General purpose (Core6 only) |

### Core6 Dimensions (always present)

| Dimension | Default Weight | Min | Max |
|-----------|---------------|-----|-----|
| accuracy | 30% | 15% | 50% |
| verifiability | 15% | 8% | 35% |
| completeness | 20% | 8% | 40% |
| clarity | 15% | 5% | 35% |
| actionability | 10% | 5% | 45% |
| relevance | 10% | 5% | 25% |

### Constraints

1. Each dimension must stay within [min, max] bounds
2. accuracy + verifiability ≥ 30% (truth anchor protection)
3. Total weights must sum to 100%
4. Additional dimensions from selected rubric can be included

### Instructions

1. **Select** the most appropriate rubric based on question intent
2. **Explain** your reasoning briefly
3. **Adjust** weights if the question has specific emphasis
4. **Validate** constraints are met

### Output Format (JSON)

{
  "selected_rubric": "<rubric_id>",
  "reasoning": "<brief explanation of why this rubric fits>",
  "confidence": <0.0-1.0>,
  "weight_adjustments": [
    {
      "dimension": "<dimension_name>",
      "original": <original_weight>,
      "adjusted": <new_weight>,
      "reason": "<why this adjustment>"
    }
  ],
  "final_weights": {
    "accuracy": <weight>,
    "verifiability": <weight>,
    "completeness": <weight>,
    "clarity": <weight>,
    "actionability": <weight>,
    "relevance": <weight>
    // additional dimensions if applicable
  }
}
```

## Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `question` | The user's original question | Yes |
| `context` | Additional context or constraints | No |

## Validation Rules

After Host LLM outputs the decision:

1. **Bounds Check**: Clip each weight to [min, max]
2. **Truth Anchor Check**: If accuracy + verifiability < 30%, proportionally increase both
3. **Normalize**: Adjust all weights to sum to 100%
4. **Record**: Log any automatic adjustments in `validation.adjustments_made`

## Notes

- If confidence < 0.5, consider using `default` rubric
- Weight adjustments should have clear reasoning tied to question content
- Additional dimensions from domain rubrics inherit their defined weights as starting point
