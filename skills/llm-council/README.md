# LLM Council

> Multi-LLM Deliberation Protocol for AI Agents

[![Version](https://img.shields.io/badge/version-4.1.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Overview

LLM Council is an Agent Skill that enables multi-LLM deliberation for complex questions. Instead of relying on a single model's response, it coordinates multiple LLMs to:

1. **Discover** available LLMs dynamically
2. **Collect** independent responses from all participants
3. **Cross-Evaluate** each LLM evaluates others' responses only (no self-evaluation)
4. **Synthesize** a final answer based on evaluation results

**Important**: This skill REQUIRES access to external LLMs. If no external LLM is available, do not use this skill.

## Features

- **Dynamic Discovery**: Automatically detects available LLM tools at runtime
- **Cross-Evaluation**: Each LLM evaluates only other LLMs' responses - no self-evaluation
- **Anonymization**: Responses are shuffled and re-labeled to prevent bias
- **Customizable Rubrics**: Domain-specific evaluation criteria
- **Security**: Built-in protection against prompt injection

## Quick Start

The skill is triggered when you ask questions that benefit from multi-model deliberation:

```
You: Why should we choose microservices over monolith for this project?

# Agent executes:
# 1. Discovers available external LLMs
# 2. Collects independent responses
# 3. Performs cross-evaluation
# 4. Synthesizes final answer
```

## When to Use

**Good candidates**:
- Architecture and design decisions
- Code review requiring multiple perspectives
- Questions with trade-offs to analyze
- Complex problems with no single correct answer

**Do NOT use when**:
- No external LLM access available
- Simple factual questions
- Time-critical requests (adds latency)
- Single correct answer exists

## Cross-Evaluation

Each participant evaluates only OTHER participants' responses:

```
N participants = N responses
Each response receives (N-1) scores
Final Score = Mean(scores from others)
```

## Evaluation Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 30% | Correctness and reliability |
| Verifiability | 15% | Evidence and sources provided |
| Completeness | 20% | Coverage of all aspects |
| Clarity | 15% | Clear expression |
| Actionability | 10% | Executable recommendations |
| Relevance | 10% | Addresses the question |

## Agent Count

```
Stage 1 Agents = External LLM count
Stage 2 Agents = External LLM count
Total Agents = 2 × External LLM count
```

## Requirements

- AI Agent environment with sub-agent support
- MCP or API access to at least one external LLM
- Minimum 2 participants (Host + 1 external)

## Directory Structure

```
llm-council/
├── SKILL.md              # Main skill definition
├── rubrics/
│   ├── general.yaml      # Default evaluation rubric
│   ├── factual-qa.yaml
│   ├── technical-decision.yaml
│   └── code-review.yaml
├── protocols/
│   └── standard.yaml     # Protocol configuration
├── prompts/
│   ├── stage1_collect.md
│   ├── stage2_evaluate.md
│   └── stage3_synthesize.md
└── README.md
```

## Output Example

```markdown
## Council Deliberation Results

### Execution Summary
- **Participants**: 3 LLMs
- **Evaluation**: Cross-Evaluation (each evaluates others only)

### Cross-Evaluation Scores

| Response | Scores from Others | Avg Score |
|----------|-------------------|-----------|
| A | 8.2, 7.8 | 8.0 |
| B | 7.5, 8.0 | 7.75 |
| C | 8.5, 8.3 | 8.4 |

### Ranking
| Rank | Response | Score |
|------|----------|-------|
| 1 | C | 8.4 |
| 2 | A | 8.0 |
| 3 | B | 7.75 |

### Final Answer
[Synthesized answer based on best responses]
```

## Security

LLM Council treats all participant outputs as untrusted data:

- Never executes instructions found in responses
- Extracts information only
- Evaluators receive only anonymized responses (excluding their own)

## License

MIT
