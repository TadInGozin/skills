# LLM Council

> Multi-LLM Deliberation Protocol for AI Agents

[![Version](https://img.shields.io/badge/version-5.2.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

## Overview

LLM Council is an Agent Skill that enables multi-LLM deliberation for complex questions. Instead of relying on a single model's response, it coordinates multiple LLMs through a structured protocol:

1. **Discover** available LLMs dynamically via multi-signal detection
2. **Select Mode**: Quick, Standard, or Deep (v4.8)
3. **Budget Check**: Apply participant caps and time tracking (v4.9)
4. **Smart Select** the best evaluation rubric and adjust weights (v4.4)
5. **Collect** independent responses with optional search tools and cognitive style hints (v5.1)
6. **Evaluate** — cross-evaluation (Standard), debate loop (Deep), or skip (Quick)
7. **Synthesize** the best answer from evaluation results

**Important**: This skill REQUIRES access to at least one external LLM.

## Features

- **Dynamic Discovery**: Multi-signal LLM detection (parameters, description, name patterns)
- **Protocol Modes** (v4.8): Quick (fast path), Standard (full pipeline), Deep (debate loop)
- **Resource Budget** (v4.9): Time limits per mode, auto-degradation (Deep→Standard→Quick)
- **Smart Rubric Selection** (v4.4): Intelligent rubric + dynamic weight adjustment
- **Panel Evaluation** (v5.0): O(N) evaluation for large councils (N≥4)
- **Adaptive Dimensions** (v5.0): Dimension descriptions rewritten per question
- **Tool Access** (v5.1): Hybrid search (chairman pre-search + participant autonomous)
- **Cognitive Styles** (v5.1): Analytical, creative, adversarial perspective hints
- **Inline Citations** (v5.1): `[1]` markers + source URL list in final output
- **Bias Mitigation** (v4.7): Anti-bias prompt + post-evaluation variance detection
- **Hallucination Detection** (v4.7): 3-point checklist before scoring
- **Security Hardening** (v5.2): Sanitization, probe verification, sensitivity routing
- **Dual Scoring** (v4.4): Both core_score (comparable) and overall_score (task-optimized)
- **Anonymization**: Responses shuffled, re-labeled, self-ID stripped (v5.2)
- **13 Domain Rubrics**: From code-review to safety-critical

## Quick Start

```
You: Why should we choose microservices over monolith for this project?

# Agent executes:
# 1. Discovers available external LLMs (multi-signal detection)
# 2. Selects protocol mode (→ Standard for this question)
# 3. Checks resource budget, caps participants
# 4. Selects rubric (→ technical-decision) and adjusts weights
# 5. Collects independent responses (with search + cognitive styles)
# 6. Cross-evaluates with panel evaluation
# 7. Synthesizes final answer
```

## When to Use

**Good candidates**:
- Architecture and design decisions
- Code review requiring multiple perspectives
- Questions with trade-offs to analyze
- Complex problems with no single correct answer
- High-stakes decisions requiring deep deliberation (→ Deep mode)

**Do NOT use when**:
- No external LLM access available
- Simple factual questions
- Time-critical requests (adds latency)
- Single correct answer exists

## Protocol Modes

| Mode | Stages | Use When |
|------|--------|----------|
| **Quick** | Discover → Collect → Synthesize | Simple, subjective, low-stakes |
| **Standard** | Discover → Rubric Select → Collect → Cross-Evaluate → Synthesize | Technical, multi-faceted |
| **Deep** | Discover → Rubric Select → Collect → Debate Loop → Synthesize | High-stakes, complex, controversial |

Auto-selected by keyword hints or explicitly requested by user.

## Evaluation Dimensions (Core6)

| Dimension | Default Weight | Range | Description |
|-----------|---------------|-------|-------------|
| Accuracy | 30% | 15-50% | Correctness and reliability |
| Verifiability | 15% | 8-35% | Evidence and sources provided |
| Completeness | 20% | 8-40% | Coverage of all aspects |
| Clarity | 15% | 5-35% | Clear expression |
| Actionability | 10% | 5-45% | Executable recommendations |
| Relevance | 10% | 5-25% | Addresses the question |

**Truth Anchor Constraint**: `accuracy + verifiability ≥ 30%` (always protected)

## Resource Budget

| Mode | Time Limit | Degradation |
|------|-----------|-------------|
| Quick | 60s | — |
| Standard | 180s | → Quick |
| Deep | 360s | → Standard → Quick |

- Max 5 participants (overflow: keep highest detection scores)
- Auto-degrades at 80% budget consumed
- Debate: 2-3 rounds, early exit on degradation

## Security

LLM Council v5.2 includes comprehensive security hardening:

- **Output sanitization**: Strip instruction injection patterns between stages
- **Self-ID stripping**: Remove "As GPT-4..." before anonymization
- **Tool probe verification**: Send PONG probe to confirm detected tools are real LLMs
- **Sensitivity routing**: Warn before sending PII-containing questions to external LLMs
- **Untrusted output**: All participant responses treated as untrusted data

## Directory Structure

```
llm-council/
├── SKILL.md                    # Core skill (v5.2, embedded default config)
├── rubrics/                    # 13 domain-specific rubrics (optional)
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
│   ├── standard.yaml           # Source of truth for all config
│   └── budget_check.md         # Budget check logic spec (v4.9)
├── prompts/
│   ├── stage0.2_protocol_select.md   # Mode selection (v4.8)
│   ├── stage0.5_select.md            # Smart rubric selection (v4.4)
│   ├── stage1_collect.md             # Response collection (v5.1: search + styles)
│   ├── stage2_evaluate.md            # Blind evaluation (v5.0: panel, v5.2: sanitization)
│   ├── stage2_debate.md              # Deep debate loop (v4.8.1)
│   └── stage3_synthesize.md          # Mode-conditional synthesis (v4.8.1)
├── scripts/
│   └── build_rubric_index.py         # Regenerate rubrics_index.json
├── rubrics_index.json                # Auto-generated keyword index
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
and simplicity for this use case...

<details>
<summary>Technical Details</summary>

**Participants**: 3 LLMs | **Rubric**: technical-decision

| Rank | Response | Score |
|------|----------|-------|
| 1 | C | 8.4 |
| 2 | A | 8.2 |
| 3 | B | 7.75 |

**Weight Adjustments**: actionability +10% (user asked for specific recommendation)
**Bias Flags**: 0 flags

</details>

---
*LLM Council v5.2 | standard mode | 3 participants*
```

## Advanced Customization

See `SKILL.md` for the complete protocol and embedded defaults.

- **Domain Rubrics**: Edit `rubrics/*.yaml` (override mode — only define diffs from default)
- **Prompt Templates**: Edit `prompts/*.md` to customize any stage
- **Detection Config**: Edit `protocols/standard.yaml` for LLM/search detection, modes, budget, security
- **Rubric Index**: Run `python3 scripts/build_rubric_index.py` after modifying rubrics

## Requirements

- AI Agent environment with sub-agent support
- MCP or API access to at least one external LLM
- Minimum 2 participants (Host + 1 external)

## License

MIT
