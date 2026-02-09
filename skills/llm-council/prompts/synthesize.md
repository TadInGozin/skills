# Stage 3: Chairman Synthesis

> **Advanced Customization**
> This file allows you to override the default synthesis prompt.
> Default templates are embedded in [SKILL.md](../SKILL.md).
> Only modify this file if you need custom behavior.

## v4.8.1 Changes

This stage is now **mode-conditional**. The template below is the **Standard** path.
Additional paths for Deep and Quick modes are appended at the end of this file.

## Template (Standard Mode)

```handlebars
As Chairman, synthesize the final answer based on the deliberation results.

## Original Question

{{question}}

## Participant Responses

{{#each responses}}
### {{provider}}'s Response (Score: {{score}})

{{{content}}}

---
{{/each}}

## Evaluation Summary

### Ranking

{{#each ranking}}
{{rank}}. **{{provider}}** - Weighted Score: {{score}}
{{/each}}

{{#if disagreements}}
### Key Disagreements

{{#each disagreements}}
- **{{topic}}**: {{description}}
  {{#if resolution}}- Resolution: {{resolution}}{{/if}}
{{/each}}
{{/if}}

## Synthesis Requirements

{{#if custom_requirements}}
{{#each synthesis_requirements}}
{{@index}}. {{this}}
{{/each}}
{{else}}
1. **Extract Core Insights**: Prioritize insights from high-scoring responses
2. **Integrate Complementary Information**: Combine unique contributions from different responses
3. **Correct Errors**: Fix any identified inaccuracies or issues
4. **Address Disagreements**: Explain how disagreements were resolved
5. **Cite Evaluator Rationale**: Reference specific evaluator feedback that influenced the synthesis (v5.0)
6. **Present Clearly**: Provide a well-structured, complete final answer
{{/if}}

{{#if include_dissent}}
- **Include Minority Views**: If significant minority opinions exist, acknowledge them
{{/if}}

## Output Structure

{{#if custom_output_format}}
{{{output_format}}}
{{else}}
### Synthesis Rationale

[Explain your synthesis approach:
- Which insights were adopted and why
- What was corrected or improved
- How disagreements were resolved]

### Key Evaluator Insights (v5.0)

[Extract the most impactful rationale from evaluators:
- Which evaluator feedback directly shaped the synthesis?
- What specific criticisms led to corrections?
- What praise confirmed which elements to keep?]

### Final Answer

[The synthesized answer - should be better than any individual response]
{{/if}}
```

## Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | Original question | Yes |
| `responses` | array | Array with {provider, content, score} | Yes |
| `ranking` | array | Sorted array with {rank, provider, score} | Yes |
| `disagreements` | array | Array of {topic, description, resolution} | No |
| `include_dissent` | boolean | Whether to include minority views | No |
| `custom_requirements` | boolean | Use custom synthesis requirements | No |
| `synthesis_requirements` | array | Custom requirements list | No |
| `custom_output_format` | boolean | Use custom output format | No |
| `output_format` | string | Custom output format template | No |

## Execution Notes

1. The final answer should be demonstrably better than individual responses
2. Do not simply concatenate responses
3. Maintain objectivity even if your response ranked lower
4. Provide transparency in synthesis reasoning

---

## Template (Deep Mode)

Use when `mode == "deep"`. Receives debate results instead of evaluation scores.

```handlebars
As Chairman, synthesize the final answer based on the debate results.

## Original Question
{{question}}

## Debate Summary
- **Rounds completed**: {{rounds_completed}}
- **Agreement score**: {{convergence_status.agreement_score}}

## Final Stances
{{#each final_stances}}
### Debater {{debater}} (Confidence: {{confidence}}, Stance: {{stance}})
{{{revised_position}}}
---
{{/each}}

{{#if convergence_status.consensus_answer}}
## Emerging Consensus
{{convergence_status.consensus_answer}}
{{/if}}

{{#if convergence_status.remaining_disagreements}}
## Unresolved Disagreements
{{#each convergence_status.remaining_disagreements}}
- {{this}}
{{/each}}
{{/if}}

## Synthesis Requirements
1. Build on the emerging consensus (if any)
2. Integrate the strongest arguments from all debaters
3. Address remaining disagreements with reasoned resolution
4. Present a well-structured final answer that reflects the depth of deliberation
```

### Deep Mode Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | Original question | Yes |
| `rounds_completed` | number | Debate rounds completed | Yes |
| `final_stances` | array | `{debater, stance, confidence, revised_position}` | Yes |
| `convergence_status` | object | `{agreement_score, consensus_answer, remaining_disagreements}` | Yes |
| `debate_log` | array | Round-by-round summaries | No |

---

## Template (Quick Mode)

Use when `mode == "quick"`. No scores or evaluation — synthesize directly from responses.

```handlebars
As Chairman, synthesize the final answer from the collected responses.

## Original Question
{{question}}

## Participant Responses
{{#each responses}}
### {{provider}}
{{{content}}}
---
{{/each}}

## Synthesis Requirements
1. Identify common ground across responses
2. Note significant differences in perspective
3. Present a concise, well-rounded answer
4. Keep it brief — this is a quick deliberation
```

### Quick Mode Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | Original question | Yes |
| `responses` | array | `{provider, content}` (no scores) | Yes |
