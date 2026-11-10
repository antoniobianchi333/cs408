# Course skill format

A skill is a folder `skills/<name>/` containing `SKILL.md`, which starts with
YAML front matter and continues with the instructions in Markdown:

```markdown
---
name: my-skill
description: When the skill is useful (shown to the agent at the start).
---

# Instructions read by the agent when the skill is relevant
```

| Field | Meaning |
| --- | --- |
| `name` | Must equal the folder name: lowercase letters, digits and hyphens. |
| `description` | Short explanation of when to use the skill; part of the initial prompt. |

The instructions (the Markdown body) are not in the initial prompt; the agent
reads `SKILL.md` when it decides the skill is relevant. Other files in the
folder, such as this one, are optional and are read only when the
instructions point to them. Skill folders must not contain symbolic links.

Select skills by folder name when running:

    python -m lab2 run --alias A --tasks garage --skills example

Omit `--skills` for a vanilla run. During the run the selected skills are at
`.skills/<name>/` in the task's working directory, so this file is
`.skills/example/references/format.md`, and a snapshot is saved in
`jobs/<alias>/<id>/skills/`.

To write your own skill, copy this folder, rename it, and change `name`,
`description` and the instructions.
