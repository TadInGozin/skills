# Stage 1: Collect Independent Response

> **Advanced Customization**
> This file allows you to override the default collection prompt.
> Default templates are embedded in [SKILL.md](../SKILL.md).
> Only modify this file if you need custom behavior.

## Template

```handlebars
{{#if custom_prompt}}
{{{custom_prompt}}}
{{else}}
Please answer the following question:

**Question**: {{question}}

{{#if requirements}}
**Requirements**:
{{#each requirements}}
- {{this}}
{{/each}}
{{else}}
**Requirements**:
- Provide a complete, accurate answer
- Clearly indicate any uncertainties
- Provide evidence or sources when possible
- Be concise but thorough
{{/if}}

{{#if context}}
**Context**:
{{context}}
{{/if}}
{{/if}}
```

## Variables

| Variable | Type | Description | Required |
|----------|------|-------------|----------|
| `question` | string | The user's original question | Yes |
| `context` | string | Additional context or constraints | No |
| `requirements` | array | Custom requirements list | No |
| `custom_prompt` | string | Fully custom prompt (replaces default) | No |

## Execution Notes

1. Send the same question to all participants
2. Do not share other participants' responses
3. Collect responses independently and in parallel when possible
4. Record response time for audit purposes
