# Stage 3: Chairman Synthesis

## Prompt Template

Use this template when synthesizing the final answer as Chairman.

---

As Chairman, synthesize the final answer based on the deliberation results.

## Original Question

{{question}}

## Participant Responses

{{#each responses}}
### {{provider}}'s Response (Score: {{score}})

{{content}}

---
{{/each}}

## Evaluation Summary

### Ranking

{{#each ranking}}
{{rank}}. **{{provider}}** - Weighted Score: {{score}}
{{/each}}

### Key Disagreements (if any)

{{#each disagreements}}
- **{{topic}}**: {{description}}
  - Resolution: {{resolution}}
{{/each}}

## Synthesis Requirements

1. **Extract Core Insights**: Prioritize insights from high-scoring responses
2. **Integrate Complementary Information**: Combine unique contributions from different responses
3. **Correct Errors**: Fix any identified inaccuracies or issues
4. **Address Disagreements**: Explain how disagreements were resolved
5. **Present Clearly**: Provide a well-structured, complete final answer

{{#if include_dissent}}
6. **Include Minority Views**: If significant minority opinions exist, acknowledge them
{{/if}}

## Output Structure

Provide the synthesis in this format:

### Synthesis Rationale

[Explain your synthesis approach:
- Which insights were adopted and why
- What was corrected or improved
- How disagreements were resolved]

### Final Answer

[The synthesized answer - should be better than any individual response]

---

## Variables

| Variable | Description |
|----------|-------------|
| `question` | Original question |
| `responses` | Array with provider, content, score |
| `ranking` | Sorted array with rank, provider, score |
| `disagreements` | Array of identified disagreements |
| `include_dissent` | Whether to include minority views |

## Notes for Execution

1. The final answer should be demonstrably better than individual responses
2. Do not simply concatenate responses
3. Maintain objectivity even if your response ranked lower
4. Provide transparency in synthesis reasoning
