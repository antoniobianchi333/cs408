# Instructions for AI coding agents

This is a CS408 Project 2 repository. Read `README.md` and follow its rules:
how to set up and run the lab2 tool, the rules for skills, and what to submit.
Never write the Purdue RCAC API key into a file, a skill, the report, or a
commit.

## AI transcripts

The group must commit the complete record of its AI use to `ai-transcripts/`
(see `ai-transcripts/README.md`). Every time you make a commit in this
repository:

1. Look for session logs of AI coding agents (Claude Code, Codex, OpenCode,
   and others) that worked in this repository and are new or changed since the
   last commit. Common places: Claude Code in `~/.claude/projects/` (a folder
   named after this repository's path), Codex in `~/.codex/sessions/` (check
   the working directory recorded in each file), and OpenCode in
   `~/.local/share/opencode/`. Include your own current session.
2. Copy the original files, unchanged and with their file names, into
   `ai-transcripts/<tool>/` (for example `ai-transcripts/claude-code/`).
   Replace an older copy of the same session.
3. Add these copies to the same commit.

If a log contains an API key or another secret, do not commit it: tell the
user first.
