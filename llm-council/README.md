# LLM Council

> Multi-LLM Deliberation Protocol for AI Agents

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Overview

LLM Council is an Agent Skill that enables multi-LLM deliberation for complex questions. Instead of relying on a single model's response, it coordinates multiple LLMs to:

1. **Collect** independent responses
2. **Evaluate** responses using blind peer review
3. **Synthesize** a final answer that's better than any individual response

## Features

- **Blind Evaluation**: Prevents self-assessment bias by anonymizing responses during evaluation
- **Customizable Rubrics**: Domain-specific evaluation criteria (code review, factual Q&A, technical decisions)
- **Verifiability Dimension**: New in v2 - evaluates whether claims are backed by evidence
- **Disqualification Rules**: Automatic handling of critical errors and fabricated references
- **Structured Output**: Detailed evaluation scores and synthesis rationale
- **Security**: Built-in protection against prompt injection

## Quick Start

### In Claude Code

The skill is triggered when you ask questions that benefit from multi-model deliberation:

```
You: Why should we choose microservices over monolith for this project?

# Claude loads llm-council skill and executes:
# 1. Generates its own response
# 2. Queries Gemini and Codex via MCP
# 3. Performs blind evaluation
# 4. Synthesizes final answer
```

### Explicit Trigger

```
/council "What's the best approach for handling authentication in our API?"
```

## When to Use

**Good candidates for LLM Council**:
- Architecture and design decisions
- Code review requiring multiple perspectives
- Questions with trade-offs to analyze
- Complex problems with no single correct answer

**Not recommended for**:
- Simple factual questions
- Tasks with clear, objective answers
- Time-critical requests (adds 2-3x latency)

## Configuration

### Rubrics

Choose the right evaluation rubric for your use case:

| Rubric | Best For | Key Focus |
|--------|----------|-----------|
| `general` | Most questions | Balanced evaluation |
| `factual-qa` | Knowledge questions | Accuracy (45%), Verifiability (25%) |
| `technical-decision` | Architecture choices | Actionability (20%) |
| `code-review` | Code audits | Security (15%), Correctness |

### Protocols

| Protocol | Stages | Use When |
|----------|--------|----------|
| `standard` | 3 (with blind eval) | Important decisions |
| `quick` | 2 (skip eval) | Time-sensitive, moderate complexity |

## Evaluation Dimensions (v2)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 30% | Correctness and reliability |
| Verifiability | 15% | Evidence and sources provided |
| Completeness | 20% | Coverage of all aspects |
| Clarity | 15% | Clear expression |
| Actionability | 10% | Executable recommendations |
| Relevance | 10% | Addresses the question |

## Requirements

- AI Agent environment (Claude Code, Codex CLI, or compatible)
- MCP connections to additional LLMs:
  - `mcp__gemini-cli__ask-gemini` or `mcp__gemini-mcp__gemini_quick_query`
  - `mcp__codex__codex`
  - Other LLM MCP servers as available

## Directory Structure

```
llm-council/
├── SKILL.md           # Main skill definition
├── rubrics/
│   ├── general.yaml   # Default evaluation rubric
│   ├── factual-qa.yaml
│   ├── technical-decision.yaml
│   └── code-review.yaml
├── protocols/
│   ├── standard.yaml  # Full 3-stage protocol
│   └── quick.yaml     # Simplified 2-stage
├── prompts/
│   ├── stage1_collect.md
│   ├── stage2_evaluate.md
│   └── stage3_synthesize.md
└── README.md
```

## Output Example

```markdown
## Council Deliberation Results

### Participants
- Response A: Claude (Host)
- Response B: Gemini
- Response C: Codex

### Ranking

| Rank | Response | Score | Source |
|------|----------|-------|--------|
| 1 | B | 8.15 | Gemini |
| 2 | C | 8.00 | Codex |
| 3 | A | 7.95 | Claude |

### Synthesis Rationale
Adopted Gemini's structured approach with Codex's implementation details...

### Final Answer
[Synthesized answer combining best insights]
```

## Security

LLM Council treats all participant outputs as untrusted data:

- Never executes instructions found in responses
- Extracts information only
- Applies sanitization before synthesis

## License

MIT

## Credits

Reviewed by: Gemini, Codex (2026-02-04)
