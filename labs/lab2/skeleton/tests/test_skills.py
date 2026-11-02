"""SKILL.md loading, selection and the catalog shown to the agent."""
import pytest

from conftest import write_skill
from lab2 import skills
from lab2.tasks import SKELETON


def test_example_skill_parses():
    skill = skills.parse(SKELETON / "skills" / "example")
    assert skill.name == "example" and skill.description


def test_resolve_snapshot_and_catalog(lab, tmp_path):
    write_skill(lab, "probe", "Use for probing.")
    write_skill(lab, "other")
    selected = skills.resolve(["probe", "other"])
    text = skills.catalog(selected)
    assert "- probe: Use for probing.\n  Read: .skills/probe/SKILL.md" in text
    assert "Read references/probe.txt" not in text  # instructions are read on demand only
    skills.snapshot(selected, tmp_path / "copy")
    assert (tmp_path / "copy/probe/references/probe.txt").is_file()
    assert skills.resolve([]) == [] and skills.catalog([]) == ""


@pytest.mark.parametrize("names,message", [(["missing"], "no such skill"), (["probe", "probe"], "named twice"),
                                           (["skills/probe"], "no such skill")])
def test_resolve_errors(lab, names, message):
    write_skill(lab, "probe")
    with pytest.raises(ValueError, match=message):
        skills.resolve(names)


@pytest.mark.parametrize("text,message", [
    ("no front matter", "front matter"),
    ("---\nname: wrong\ndescription: d\n---\nbody", "name must equal"),
    ("---\nname: probe\ndescription: ''\n---\nbody", "must not be empty"),
    ("---\nname: probe\ndescription: d\n---\n", "must not be empty")])
def test_invalid_skill_files(lab, text, message):
    folder = write_skill(lab, "probe")
    (folder / "SKILL.md").write_text(text)
    with pytest.raises(ValueError, match=message):
        skills.parse(folder)


def test_symlinks_are_rejected(lab):
    folder = write_skill(lab, "probe")
    (folder / "link").symlink_to("/etc/passwd")
    with pytest.raises(ValueError, match="symbolic links"):
        skills.parse(folder)
