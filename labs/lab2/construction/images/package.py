"""Package a built udocker container as a udocker-loadable image archive.

    from package import package
    package(container_dir, tag, env, labels, out_file)     # out_file: <id>-arm64.tar.gz

The archive is a single-layer `docker save` tarball with v1 layer metadata
(<layer>/VERSION, <layer>/json, repositories) so that `udocker load -i` (1.3.17)
accepts it, compressed with `gzip -n -6`. Before packing, build caches, /tmp,
__pycache__/.pytest_cache under /app and the git reflog are removed; the /app
working tree must be clean. Nothing else (host mounts, tests, patches, reports)
is added.
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import tarfile
from pathlib import Path


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def _root_owned(info):
    info.uid = info.gid = 0
    info.uname = info.gname = "root"
    return info


def _clean(root):
    for rel in ("root/.cache", "tmp"):
        shutil.rmtree(root / rel, ignore_errors=True)
        (root / rel).mkdir()
    os.chmod(root / "tmp", 0o1777)
    for cache in [*(root / "app").rglob("__pycache__"), *(root / "app").rglob(".pytest_cache")]:
        shutil.rmtree(cache, ignore_errors=True)
    app = str(root / "app")
    subprocess.run(["git", "-C", app, "reflog", "expire", "--expire=now", "--all"], check=True)
    subprocess.run(["git", "-C", app, "gc", "--prune=now", "-q"], check=True)
    dirty = subprocess.run(["git", "-C", app, "status", "--porcelain"], capture_output=True, text=True, check=True).stdout
    if dirty.strip():
        raise RuntimeError("/app working tree is not clean:\n" + dirty)


def package(container, tag, env, labels, out_file):
    """Write out_file (.tar.gz) from container/ROOT with the given image config."""
    container, out_file = Path(container), Path(out_file)
    root = container / "ROOT"
    _clean(root)
    config = json.loads((container / "container.json").read_text())["config"]
    config.update({"Env": [f"{k}={v}" for k, v in env.items()], "Labels": labels, "WorkingDir": "/app", "Cmd": ["/bin/bash"]})

    out_file.parent.mkdir(parents=True, exist_ok=True)
    layer = out_file.with_name(out_file.name + ".layer.tar")
    with tarfile.open(layer, "w", format=tarfile.PAX_FORMAT) as tar:
        for entry in sorted(root.iterdir()):
            if entry.name not in ("proc", "sys", "dev"):
                tar.add(entry, arcname=entry.name, filter=_root_owned)
        for name in ("proc", "sys", "dev"):  # empty mount points
            info = tarfile.TarInfo(name)
            info.type, info.mode = tarfile.DIRTYPE, 0o755
            tar.addfile(info)
    layer_id = _sha256(layer)

    image = {"architecture": "arm64", "os": "linux", "config": config,
             "rootfs": {"type": "layers", "diff_ids": ["sha256:" + layer_id]}}
    config_raw = json.dumps(image, sort_keys=True).encode()
    config_id = hashlib.sha256(config_raw).hexdigest()
    repo, version = tag.rsplit(":", 1)
    meta = [
        (config_id + ".json", config_raw),
        ("manifest.json", json.dumps([{"Config": config_id + ".json", "RepoTags": [tag],
                                       "Layers": [layer_id + "/layer.tar"]}]).encode()),
        (layer_id + "/VERSION", b"1.0"),
        (layer_id + "/json", json.dumps(dict(image, id=layer_id)).encode()),
        ("repositories", json.dumps({repo: {version: layer_id}}).encode()),
    ]
    plain = out_file.with_suffix("")  # <id>-arm64.tar
    with tarfile.open(plain, "w") as tar:
        tar.add(layer, arcname=layer_id + "/layer.tar", filter=_root_owned)
        for name, data in meta:
            info = tarfile.TarInfo(name)
            info.size, info.mode = len(data), 0o644
            tar.addfile(info, io.BytesIO(data))
    layer.unlink()
    out_file.unlink(missing_ok=True)
    subprocess.run(["gzip", "-n", "-6", str(plain)], check=True)  # replaces plain with out_file
    return out_file
