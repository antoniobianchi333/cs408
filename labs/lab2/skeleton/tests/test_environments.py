"""The default image store: a private folder of this user under the temporary directory."""
import os
import pwd
import tempfile

import pytest

from lab2 import environments
from lab2.environments import image_store


def test_default_store_is_private_to_the_user(tmp_path, monkeypatch):
    monkeypatch.delenv("LAB2_IMAGE_STORE", raising=False)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    base = tmp_path / f"cs408-lab2-{pwd.getpwuid(os.getuid()).pw_name}"

    assert image_store() == base / "udocker"
    assert base.stat().st_mode & 0o777 == 0o700
    assert image_store() == base / "udocker"  # an existing folder of the user is reused

    base.rmdir()
    base.symlink_to(tmp_path)  # a name taken by a link is refused
    with pytest.raises(RuntimeError, match="not a folder of yours"):
        image_store()


def test_store_from_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("LAB2_IMAGE_STORE", str(tmp_path / "store"))
    assert image_store() == tmp_path / "store"


def test_shared_store_is_used_only_when_others_cannot_write_to_it(tmp_path, monkeypatch):
    shared = tmp_path / "shared"
    monkeypatch.setattr(environments, "SHARED_STORE", shared)
    assert environments.shared_store() is None  # missing

    for d in ("repos", "layers"):
        (shared / d).mkdir(parents=True)
    os.chmod(shared, 0o755)
    assert environments.shared_store() == shared

    os.chmod(shared / "layers", 0o777)  # others could replace the images
    assert environments.shared_store() is None


def test_pulled_images_are_removed_when_the_last_command_ends(tmp_path, monkeypatch):
    store = tmp_path / "store"
    monkeypatch.setenv("LAB2_IMAGE_STORE", str(store))
    with environments.own_images():
        (store / "layers").mkdir()
        (store / "layers" / "blob").write_text("image")
        assert not environments.remove_own_images(store)  # this command still runs
    assert not (store / "layers").exists() and not list(store.glob("lab2-command-*"))
