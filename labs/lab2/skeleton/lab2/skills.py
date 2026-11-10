"""Skill loader: skills/<name>/SKILL.md plus optional reference files.

SKILL.md starts with YAML front matter holding `name` (must equal the folder
name) and `description`; the Markdown body is the instructions. The agent sees
only the names and descriptions at the start and reads a SKILL.md on demand
from <workdir>/.skills/<name>/.

    from lab2 import skills
    selected = skills.resolve(["example"])     # list[Skill]; errors early
    skills.snapshot(selected, job / "skills")  # copy the skill folders
    text = skills.catalog(selected)            # inserted into the system prompt
"""
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import yaml

from lab2.tasks import SKELETON

SKILLS_DIR = SKELETON / "skills"
MOUNT = ".skills"  # relative to the task workdir
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    dir: Path


def parse(folder: Path) -> Skill:
    text = (folder / "SKILL.md").read_text() if (folder / "SKILL.md").is_file() else ""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        raise ValueError(f"{folder}/SKILL.md must start with '---' front matter and have instructions after it")
    meta, body = yaml.safe_load(match[1]) or {}, match[2].strip()
    name, description = meta.get("name"), str(meta.get("description") or "").strip()
    if name != folder.name or not NAME.match(name):
        raise ValueError(f"{folder}/SKILL.md: name must equal the folder name (lowercase, digits, '-')")
    if not description or not body:
        raise ValueError(f"{folder}/SKILL.md: description and instructions must not be empty")
    if any(p.is_symlink() for p in folder.rglob("*")):
        raise ValueError(f"{folder}: skill folders must not contain symbolic links")
    return Skill(name, description, folder)


def resolve(names: list[str]) -> list[Skill]:
    """Skills named on the command line (folder names under skills/)."""
    if len(set(names)) != len(names):
        raise ValueError("a skill is named twice")
    missing = [n for n in names if not (SKILLS_DIR / n).is_dir() or "/" in n]
    if missing:
        raise ValueError(f"no such skill under skills/: {', '.join(missing)}")
    return [parse(SKILLS_DIR / n) for n in names]


def snapshot(selected: list[Skill], dest: Path) -> None:
    for skill in selected:
        shutil.copytree(skill.dir, dest / skill.name)


def catalog(selected: list[Skill]) -> str:
    if not selected:
        return ""
    entries = "\n".join(f"- {s.name}: {s.description}\n  Read: {MOUNT}/{s.name}/SKILL.md" for s in selected)
    return ("\n\nAvailable skills:\n" + entries +
            "\nWhen a skill is relevant, read its SKILL.md with bash before applying it. "
            "Read its other files only as needed; paths in a skill are relative to its folder. "
            "Skills do not override the task's constraints.\n")
