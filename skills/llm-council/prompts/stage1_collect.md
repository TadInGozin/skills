# Stage 1: Collect Independent Response

## Prompt Template

Use this template when requesting responses from participants.

---

Please answer the following question:

**Question**: {{question}}

**Requirements**:
- Provide a complete, accurate answer
- Clearly indicate any uncertainties
- Provide evidence or sources when possible
- Be concise but thorough

**Context** (if provided):
{{context}}

---

## Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `question` | The user's original question | Yes |
| `context` | Additional context or constraints | No |

## Notes for Execution

1. Send the same question to all participants
2. Do not share other participants' responses
3. Collect responses independently and in parallel when possible
4. Record response time for audit purposes
