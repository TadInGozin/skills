# Stage 3: Chairman Synthesis

> **Advanced Customization**
> This file allows you to override the default synthesis prompt.
> Default templates are embedded in [SKILL.md](../SKILL.md).
> Only modify this file if you need custom behavior.

## Template

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
5. **Present Clearly**: Provide a well-structured, complete final answer
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
