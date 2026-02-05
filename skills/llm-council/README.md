# LLM Council

> Multi-LLM Deliberation Protocol for AI Agents

[![Version](https://img.shields.io/badge/version-4.4.1-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Overview

LLM Council is an Agent Skill that enables multi-LLM deliberation for complex questions. Instead of relying on a single model's response, it coordinates multiple LLMs to:

1. **Discover** available LLMs dynamically
2. **Smart Select** the best evaluation rubric and adjust weights (v4.4)
3. **Collect** independent responses from all participants
4. **Cross-Evaluate** each LLM evaluates others' responses only (no self-evaluation)
5. **Synthesize** a final answer based on evaluation results

**Important**: This skill REQUIRES access to external LLMs. If no external LLM is available, do not use this skill.

## Features

- **Dynamic Discovery**: Automatically detects available LLM tools at runtime
- **Smart Rubric Selection** (v4.4): Host LLM intelligently selects rubric and adjusts weights
- **Dynamic Weight Adjustment** (v4.4): Weights optimized for specific question intent
- **Dual Scoring** (v4.4): Both core_score (comparable) and overall_score (task-optimized)
- **Cross-Evaluation**: Each LLM evaluates only other LLMs' responses - no self-evaluation
- **Anonymization**: Responses are shuffled and re-labeled to prevent bias
- **Customizable Rubrics**: 13 domain-specific evaluation criteria
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

## Evaluation Dimensions (Core6)

| Dimension | Default Weight | Range | Description |
|-----------|---------------|-------|-------------|
| Accuracy | 30% | 15-50% | Correctness and reliability |
| Verifiability | 15% | 8-35% | Evidence and sources provided |
| Completeness | 20% | 8-40% | Coverage of all aspects |
| Clarity | 15% | 5-35% | Clear expression |
| Actionability | 10% | 5-45% | Executable recommendations |
| Relevance | 10% | 5-25% | Addresses the question |

**v4.4 Dynamic Weights**: Weights are adjusted within these ranges based on question intent.
- **Truth Anchor Constraint**: `accuracy + verifiability ≥ 30%` (always protected)

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

## Smart Rubric Selection (v4.4)

Instead of keyword matching, the Host LLM intelligently analyzes each question to:

1. **Select** the most appropriate rubric from 13 domain options
2. **Adjust** dimension weights based on question emphasis
3. **Validate** constraints are met (tiered floors, truth anchor protection)
4. **Output** both core_score and overall_score for comparison

Example: For a question like "Review this API for security vulnerabilities and performance":
- Selected rubric: `code-review`
- Weight adjustments: `security: +10%`, `actionability: +5%`
- Both scores calculated for cross-task comparison

## Configuration Architecture

LLM Council v4.4 uses an "embedded core + external extension" architecture:

**Core (SKILL.md)**
- Contains complete default evaluation rubric
- Fully functional without external files
- Self-documented with all embedded settings

**External Extensions (Optional)**
- `rubrics/*.yaml` - Domain overrides (only differences from default)
- `prompts/*.md` - Customizable prompt templates
- `protocols/standard.yaml` - Resource manifest and detection rules

**Rubric Selection Priority**
1. **Manual** - User explicitly requests a rubric type
2. **Auto-detect** - Question content matched against keywords
3. **Default** - Embedded rubric in SKILL.md

## Directory Structure

```
llm-council/
├── SKILL.md              # Core skill (embedded default config)
├── rubrics/              # 13 domain-specific rubrics (optional)
│   ├── code-review.yaml
│   ├── factual-qa.yaml
│   ├── technical-decision.yaml
│   ├── debugging.yaml
│   ├── summarization.yaml
│   ├── creative-writing.yaml
│   ├── brainstorming.yaml
│   ├── translation.yaml
│   ├── instructional.yaml
│   ├── information-extraction.yaml
│   ├── project-planning.yaml
│   ├── customer-support.yaml
│   └── safety-critical.yaml
├── protocols/
│   └── standard.yaml     # Resource manifest + weight constraints
├── prompts/              # External prompt templates
│   ├── stage0.5_select.md  # Smart rubric selection (v4.4)
│   ├── stage1_collect.md
│   ├── stage2_evaluate.md
│   └── stage3_synthesize.md
└── README.md
```

## Output Example

```markdown
## Council Deliberation Results

### Final Answer
Based on our analysis, we recommend using Redis for session caching due to
its superior performance characteristics and built-in TTL support...

### Why This Answer
All three evaluators agreed that Redis offers the best balance of performance
and simplicity for this use case. While one participant suggested Memcached
for its slightly lower memory footprint, the consensus was that Redis's
additional features (persistence, pub/sub) provide valuable optionality
without significant overhead.

<details>
<summary>Technical Details</summary>

**Participants**: 3 LLMs | **Rubric**: technical-decision

| Rank | Response | Score |
|------|----------|-------|
| 1 | C | 8.4 |
| 2 | A | 8.2 |
| 3 | B | 7.75 |

**Weight Adjustments**: actionability +10% (user asked for specific recommendation)

</details>

---
*LLM Council v4.4 | 3 participants*
```

## Security

LLM Council treats all participant outputs as untrusted data:

- Never executes instructions found in responses
- Extracts information only
- Evaluators receive only anonymized responses (excluding their own)

## Advanced Customization

For customization options, see `SKILL.md` which contains the complete protocol and embedded defaults.

**Custom Domain Rubrics**

Domain rubrics in `rubrics/` use override mode - they only define dimensions that differ from the default. Example:

```yaml
# rubrics/code-review.yaml - adds security dimension
mode: override
dimensions:
  security:
    weight: 15
    description: "Security best practices"
```

**Custom Prompts**

Edit prompt templates in `prompts/` to customize response collection, evaluation, or synthesis behavior.

**Detection Keywords**

Edit `protocols/standard.yaml` to modify auto-detection keywords for different rubric types.

## License

MIT
