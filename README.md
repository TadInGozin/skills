# Agent Skills Marketplace

A Claude Code plugin marketplace for agent skills.

## Installation

```bash
# Add this marketplace
/plugin marketplace add TadInGozin/skills

# Install decision-making skills (includes llm-council)
/plugin install decision-making-skills@tadingozin-skills
```

## Available Plugins

### decision-making-skills

Skills for multi-model deliberation, consensus building, and decision support.

| Skill | Description |
|-------|-------------|
| llm-council | Multi-LLM deliberation protocol that coordinates multiple LLMs to provide independent responses, evaluate them blindly, and synthesize a final answer |

## Contributing

To add a new skill:

1. Create a folder under `skills/<skill-name>/`
2. Add a `SKILL.md` with frontmatter and instructions
3. Update `.claude-plugin/marketplace.json` to include your skill in the appropriate plugin category

## License

MIT
