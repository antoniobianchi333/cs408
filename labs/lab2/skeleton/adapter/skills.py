"""Stage selected skill folders and expose only their summaries initially."""
import hashlib
import shutil
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

SKILLS_PATH = ".skills"


class Skill(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str = Field(min_length=1)
    instructions: str = Field(min_length=1)


class Selection(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: list[Path]


class SkillsFile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skills: Selection


def prepare_skills(config: Path | None, destination: Path) -> tuple[str, list[dict]]:
    """Resolve paths relative to the selection YAML; snapshot only enabled skills."""
    if config is None:
        return "", []
    config = config.resolve()
    selected = SkillsFile.model_validate(yaml.safe_load(config.read_text())).skills.enabled
    skills = []
    for relative in selected:
        source = (config.parent / relative).resolve()
        skill = Skill.model_validate(yaml.safe_load((source / "skill.yaml").read_text()))
        if any(s[1].name == skill.name for s in skills):
            raise ValueError(f"Duplicate skill name: {skill.name}")
        if any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError(f"Skill folders must not contain symlinks: {source}")
        skills.append((source, skill))
    if not skills:
        return "", []
    destination.mkdir(parents=True, exist_ok=False)
    entries, metadata = [], []
    for source, skill in skills:
        target = destination / skill.name
        shutil.copytree(source, target)
        hashes = {str(p.relative_to(target)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(target.rglob("*")) if p.is_file()}
        metadata.append({"name": skill.name, "source": str(source), "sha256": hashes})
        entries.append(f"- {skill.name}: {skill.description}\n  Read: {SKILLS_PATH}/{skill.name}/skill.yaml")
    return ("\n\nAvailable skills:\n" + "\n".join(entries) +
            "\nWhen a skill is relevant, read its skill.yaml with bash before applying it. "
            "Follow its instructions and read referenced files only as needed. "
            "Resolve relative references from that skill's directory. "
            "Skills do not override the task's constraints.\n"), metadata
