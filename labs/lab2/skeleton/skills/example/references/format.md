# Course skill format

Each skill is a directory containing `skill.yaml`. All three fields are required:

| Field | Meaning |
| --- | --- |
| `name` | Unique lowercase identifier, such as `example` or `my-skill`. Digits and hyphens are allowed. |
| `description` | Short explanation of when the skill is useful. Visible in the initial skill catalog. |
| `instructions` | Full instructions, written as a YAML multiline string. Read by the agent when needed. |

Additional YAML fields are rejected. A run cannot select two skills with the same
name. Supporting files are optional; this example uses `references/format.md`.
They are copied with the selected skill, but are not automatically inserted into
the prompt. Do not include symbolic links in a skill directory.

A skill-list file selects directories, not individual YAML files:

```yaml
skills:
  enabled:
    - ../skills/example
    # - ../skills/another-skill
```

The directory paths are relative to the **skill-list file**, not the shell's
working directory. For `skillsets/example.yaml`, `../skills/example` selects this
directory. At runtime the selected copy is available at `.skills/example/` in the
task workspace. Paths mentioned inside a skill's instructions are relative to
that skill's directory; for example, this file is
`.skills/example/references/format.md`.

A directory under `skills/` is not enabled just because it exists. Select a list
explicitly with `--skills-config skillsets/example.yaml`. Omit `--skills-config`
to disable skills entirely for a vanilla run.

To create your own skill, copy this directory, change its `name`, `description`,
and `instructions`, and select its directory in a skill-list YAML. Supporting
files may be added or removed as needed. This example contains no task-specific
testing advice.
