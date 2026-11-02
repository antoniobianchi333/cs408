"""Build, check, package and validate the ARM64 task images.

    python construction/images/build.py [TASK ...] [--out DIR] [--work DIR] [--no-validate]
    python construction/images/build.py --check [TASK ...]      only check that every source is reachable

Every image starts from a copy of the local mars-base ARM64 container
(~/.udocker/containers/cs408-mars-arm64, never modified) and is built from
public sources only:
  * SWE-Atlas TW tasks (paperless, minio, k6): /app is the /app tree of the
    task's Atlas x86 image (its layers are streamed from the registry; only /app
    is taken), plus native ARM64 toolchains and dependencies;
  * DeepSWE tasks (dateutil, psd-tools, abs): the DeepSWE environment recipe
    (source/Dockerfile): clone the repository at the base commit with no future
    history, then install the dependencies.
Python dependencies are pinned by the task's source/constraints.txt or
source/requirements.txt (the versions the images were validated with).

The built /app must match task.yaml `environment.head` and the recorded tree
(`app_tree` below, `git rev-parse HEAD^{tree}`), with a clean working tree.
The image is packaged as <out>/<id>-arm64.tar.gz (tag cs408-lab2/<id>:arm64),
loaded into the image store <out>/udocker and validated with
construction/validate.py (the official checks of the source task).

Each build holds one container copy (~100k inodes) in --work; tasks are built
one at a time and the container is removed after packaging. Needs network
access (registry, GitHub, go.dev, PyPI, Debian, Go module proxy).
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONSTRUCTION = HERE.parent
sys.path[:0] = [str(HERE), str(CONSTRUCTION.parent / "skeleton")]  # package.py, the lab2 package
from lab2 import tasks  # noqa: E402
from lab2.environments import Udocker, normalize_tree  # noqa: E402
from package import package  # noqa: E402

SEED = Path.home() / ".udocker/containers/cs408-mars-arm64"
ATLAS = "ghcr.io/scaleapi/swe-atlas-v1.1:"
# Go settings baked into the Go images (lab2.tasks.GO_ENV overrides them at run time, always offline).
GO_BUILD_ENV = {"GOMAXPROCS": "4", "GOFLAGS": "-p=4", "GOTOOLCHAIN": "local", "HOME": "/root"}
# Module downloads during the build of recipes with "go_build": True.
GO_PROXY = {"GOPROXY": "https://proxy.golang.org,direct", "GOSUMDB": "sum.golang.org"}
# The Atlas Go images run offline with the module cache baked in.
GO_OFFLINE = {"GOPROXY": "off", "GOSUMDB": "off"}
VENV = "/opt/task-venv"
UV = f"uv pip install --no-cache --python {VENV}/bin/python"
B = "/tmp/lab2-build"  # the task's source/ files, inside the build container


def data_dir(task):
    """construction/tasks/<type>/<id>/: the task's source/ files (and reference-tests/ of the Atlas tasks)."""
    return CONSTRUCTION / "tasks" / task.type / task.id


def task_ids(selected=()):
    """The given image task ids, or all of them; unknown ids raise."""
    unknown = sorted(set(selected) - set(RECIPES))
    if unknown:
        raise SystemExit(f"unknown image task(s) {', '.join(unknown)}; known: {', '.join(RECIPES)}")
    return list(selected) or list(RECIPES)

# DeepSWE environment recipe (source/Dockerfile): the default branch points at the
# base commit, future commits and tags are removed, hooks are disabled.
CLONE = """set -e
cd /app
git clone {repository} .
DEFAULT="$(git remote show origin | sed -n 's/.*HEAD branch: //p')"
git checkout -B "$DEFAULT" {base_commit}
git remote remove origin
for b in $(git for-each-ref --format='%(refname:short)' refs/heads | grep -vx "$DEFAULT"); do git branch -D "$b" || true; done
for t in $(git tag); do git merge-base --is-ancestor "$t" HEAD 2>/dev/null || git tag -d "$t"; done
git reflog expire --expire=now --all
git gc --prune=now
(git submodule update --init --recursive || true)
git config core.hooksPath /dev/null
"""

# Per task: "atlas" (Atlas image whose /app is taken; else the DeepSWE clone), "go" (Go
# toolchain version to install), "app_tree" (expected tree of /app), "env" (final image
# environment), "go_build" (Go modules are downloaded during the build) and "install" commands.
RECIPES = {
    "paperless": {
        "atlas": "swe_atlas_TW_paperless-ngx_paperless-ngx_6902ef3ab97fe23e2ad27271_1.1"
                 "@sha256:240757e3074a7002cbcc99ba85702c511bfcdf40b28f8ee9f6021b8ba7a713f8",
        "app_tree": "15d567e70c83b383133c50ee8c660c96ccc8583f",
        "env": {"PATH": VENV + "/bin:", "PAPERLESS_DISABLE_DBHANDLER": "true", "PAPERLESS_CI_TEST": "1",
                "DJANGO_SETTINGS_MODULE": "paperless.settings",
                "PAPERLESS_CACHE_BACKEND": "django.core.cache.backends.locmem.LocMemCache", "HOME": "/root"},
        "install": [
            "apt-get update -qq && apt-get install -y -qq libmagic1",  # python-magic needs libmagic
            "uv python install --install-dir /opt/python 3.9.25",
            f"uv venv {VENV} --python /opt/python/cpython-3.9.25-linux-aarch64-gnu/bin/python3.9",
            f"{UV} pip==25.3 setuptools==62.1.0 wheel==0.48.0",  # bootstrap pins (as in the validated image), no -c
            # requirements.txt from PyPI only (no piwheels index); psycopg2 as its binary wheel (the
            # tests use SQLite); pikepdf/ocrmypdf have no aarch64 wheel and are only used by OCR/PDF parsing.
            "grep -v -E '^(-i |--extra-index-url )' requirements.txt | sed -E 's/^psycopg2==/psycopg2-binary==/'"
            f" | grep -v -E '^(pikepdf|ocrmypdf)==' > {B}/requirements.txt",
            f"{UV} -r {B}/requirements.txt",  # fully pinned (pipenv lock); later steps apply constraints.txt
            f"{UV} -c {B}/constraints.txt pytest pytest-django pytest-env pytest-cov pytest-xdist",
            # Atlas' removal of the reference tests also dropped two decorators of pre-existing tests.
            f"GIT_COMMITTER_NAME=CS408 GIT_COMMITTER_EMAIL=cs408@localhost git am --committer-date-is-author-date"
            f" {B}/restore-decorators.patch",
        ],
    },
    "minio": {
        "atlas": "swe_atlas_TW_minio_minio_6902ef3ab97fe23e2ad271f9_1.1"
                 "@sha256:1fa48d8ea2b5883ba04ff5e36e0e1dd53c920aac79ac33d02c422238007fd486",
        "go": "1.24.3",
        "app_tree": "bc21352e5cc5d8351457ab8e590cbd3e020267ce",
        "env": {**GO_BUILD_ENV, **GO_OFFLINE},
        "go_build": True,
        "install": ["go version && go mod download"],
    },
    "k6": {
        "atlas": "swe_atlas_TW_grafana_k6_6902ef3ab97fe23e2ad27275_1.1"
                 "@sha256:8465c1064538c0113bdb55f7fcb400c56bfe9d473a84edc0e69282ea99459557",
        "go": "1.23.10",
        "app_tree": "bd3b9d0dbf08c07fdcf4c73180e1c1b3242b0b10",
        "env": {**GO_BUILD_ENV, **GO_OFFLINE},
        "go_build": True,
        "install": ["go version && go mod download"],
    },
    "dateutil": {
        "app_tree": "392eba1d2f7e0c6238d3d9246a6b48da7268cf24",
        "env": {},
        "install": [
            # The zoneinfo tarball is not in git; it comes from the last sdist that ships it.
            "echo src/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz >> .git/info/exclude",
            f"mkdir -p src/dateutil/zoneinfo {B}/sdist && pip3 download --no-cache-dir python-dateutil==2.9.0.post0"
            f" --no-deps --no-binary :all: -d {B}/sdist -q && tar xzf {B}/sdist/python?dateutil-*.tar.gz -C {B}/sdist"
            f" && cp {B}/sdist/python?dateutil-*/src/dateutil/zoneinfo/dateutil-zoneinfo.tar.gz src/dateutil/zoneinfo/",
            f"pip3 install --no-cache-dir -c {B}/constraints.txt -e . && pip3 install --no-cache-dir"
            f" -c {B}/constraints.txt -r requirements-dev.txt pytest",
        ],
    },
    "psd-tools": {
        "app_tree": "ae624f8a0061d93497e03248a65223a8881df05f",
        "env": {"PATH": VENV + "/bin:", "PYTHONPATH": "/app/src"},
        "install": [f"uv venv {VENV} --python /usr/local/bin/python3 && {UV} -r {B}/requirements.txt"],
    },
    "abs": {
        "app_tree": "0c2b24c8a6c49eb7fffb1747eb08177175cb742d",  # Go from mars-base (1.25.5)
        "env": {**GO_BUILD_ENV, **GO_PROXY},
        "go_build": True,
        "install": ["go mod download && go install github.com/ctrf-io/go-ctrf-json-reporter/cmd/go-ctrf-json-reporter@v0.1.0"],
    },
}


# ---------------------------------------------------------------- sources

def _open(url, headers):
    """GET with anonymous registry token negotiation."""
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120)
    except urllib.error.HTTPError as e:
        if e.code != 401:
            raise
        params = dict(re.findall(r'(\w+)="([^"]*)"', e.headers["WWW-Authenticate"]))
        realm = params.pop("realm")
        token = json.load(urllib.request.urlopen(realm + "?" + urllib.parse.urlencode(params), timeout=60))
        headers["Authorization"] = "Bearer " + (token.get("token") or token["access_token"])
        return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120)


def atlas_layers(ref):
    """(base url, headers, layer descriptors) of the linux/amd64 Atlas image `ref`."""
    host, rest = ref.split("/", 1)
    name, digest = rest.split("@")
    repo = name.rsplit(":", 1)[0]
    headers = {"Accept": ", ".join("application/vnd." + t for t in (
        "oci.image.manifest.v1+json", "docker.distribution.manifest.v2+json",
        "oci.image.index.v1+json", "docker.distribution.manifest.list.v2+json"))}
    base = f"https://{host}/v2/{repo}"
    manifest = json.load(_open(f"{base}/manifests/{digest}", headers))
    if "manifests" in manifest:  # multi-platform index
        digest = next(m["digest"] for m in manifest["manifests"] if m["platform"]["architecture"] == "amd64")
        manifest = json.load(_open(f"{base}/manifests/{digest}", headers))
    return base, headers, manifest["layers"]


def extract_app(ref, root):
    """Replay the /app entries of every layer of `ref` into root/app (whiteouts applied)."""
    base, headers, layers = atlas_layers(ref)
    for layer in layers:
        with _open(f"{base}/blobs/{layer['digest']}", dict(headers)) as blob, tarfile.open(fileobj=blob, mode="r|*") as tar:
            for m in tar:
                name = m.name[2:] if m.name.startswith("./") else m.name.lstrip("/")
                if not (name == "app" or name.startswith("app/")) or ".." in Path(name).parts:
                    continue
                path = root / name
                if path.name == ".wh..wh..opq":  # opaque directory: drop what lower layers put there
                    for child in path.parent.iterdir():
                        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
                    continue
                if path.name.startswith(".wh."):
                    target = path.parent / path.name[4:]
                    if target.is_dir() and not target.is_symlink():
                        shutil.rmtree(target)
                    elif target.exists() or target.is_symlink():
                        target.unlink()
                    continue
                if not m.isdir() and (path.is_symlink() or path.exists()):
                    shutil.rmtree(path) if path.is_dir() and not path.is_symlink() else path.unlink()
                if m.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                    path.chmod(m.mode | 0o700)
                elif m.issym():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.symlink_to(m.linkname)
                elif m.islnk():
                    shutil.copy2(root / m.linkname.lstrip("./"), path)
                elif m.isfile():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(m) as src, open(path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    path.chmod(m.mode | 0o600)
        print(f"  layer {layer['digest'][7:19]} ({layer['size'] >> 20} MiB) applied", flush=True)


def go_toolchain(version, cache, root):
    """Install the official linux-arm64 Go `version` (checksum from go.dev) as root/usr/local/go."""
    name = f"go{version}.linux-arm64.tar.gz"
    releases = json.load(urllib.request.urlopen("https://go.dev/dl/?mode=json&include=all", timeout=60))
    expected = next(f["sha256"] for r in releases if r["version"] == "go" + version for f in r["files"] if f["filename"] == name)
    archive = cache / name
    if not archive.exists():
        urllib.request.urlretrieve("https://go.dev/dl/" + name, archive)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
        raise RuntimeError(f"{name}: checksum mismatch")
    shutil.rmtree(root / "usr/local/go")
    with tarfile.open(archive) as tar:
        tar.extractall(root / "usr/local", filter="data")


# ---------------------------------------------------------------- build

def image_env(seed_env, recipe_env):
    """Final image environment: the seed's, without build-only entries, plus the recipe's."""
    env = dict(e.split("=", 1) for e in seed_env)
    env.pop("PIP_BREAK_SYSTEM_PACKAGES", None)
    env["PATH"] = ":".join(p for p in env["PATH"].split(":") if p not in ("/root/.cargo/bin", "/root/.rye/shims", "/root/.bun/bin"))
    for key, value in recipe_env.items():
        env[key] = value + env["PATH"] if key == "PATH" else value  # PATH entries are prefixes
    return env


def build(task, out, work, validate):
    recipe, spec = RECIPES[task.id], task.spec
    udocker = Udocker(work / "store")
    containers = udocker.store / "containers"
    containers.mkdir(parents=True, exist_ok=True)
    name = "build-" + task.id
    udocker.remove(name)
    target = containers / str(uuid.uuid4())
    print(f"{task.id}: copying the mars-base container", flush=True)
    shutil.copytree(SEED.resolve(), target, symlinks=True, ignore=shutil.ignore_patterns(".mountpoints"))
    (containers / name).symlink_to(target.name)
    try:
        root = target / "ROOT"
        normalize_tree(root, writable_files=True)
        shutil.rmtree(root / "app", ignore_errors=True)
        (root / "app").mkdir()
        shutil.copytree(data_dir(task) / "source", root / B.lstrip("/"))
        config_path = target / "container.json"
        config = json.loads(config_path.read_text())
        final_env = image_env(config["config"]["Env"], recipe["env"])
        build_env = {**final_env, "PIP_BREAK_SYSTEM_PACKAGES": "1"}
        if recipe.get("go_build"):
            build_env.update(GO_PROXY)
        config["config"]["Env"] = [f"{k}={v}" for k, v in build_env.items()]
        config_path.write_text(json.dumps(config))

        if "atlas" in recipe:
            print(f"{task.id}: extracting /app from the Atlas image", flush=True)
            extract_app(ATLAS + recipe["atlas"], root)
            steps = []
        else:
            steps = [CLONE.format(**spec["source"])]
        if recipe.get("go"):
            go_toolchain(recipe["go"], work, root)
        for step in steps + recipe["install"]:
            print(f"{task.id}: $ {step.splitlines()[-1][:110]}", flush=True)
            subprocess.run(udocker.run_args(name, "/app", {}) + ["bash", "-c", step], env=udocker.env, check=True)

        git = lambda *a: subprocess.run(["git", "-C", str(root / "app"), *a], capture_output=True, text=True, check=True).stdout.strip()
        head, tree, dirty = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}"), git("status", "--porcelain")
        if (head, tree, dirty) != (spec["environment"]["head"], recipe["app_tree"], ""):
            raise RuntimeError(f"{task.id}: /app is HEAD {head} tree {tree} (dirty: {bool(dirty)}); expected "
                               f"{spec['environment']['head']} tree {recipe['app_tree']}")
        archive = out / spec["environment"]["archive"]
        labels = {"org.opencontainers.image.title": task.id, "cs408.task": task.id,
                  "cs408.source": f"{spec['source']['dataset']} {spec['source']['task']}"}
        print(f"{task.id}: packaging {archive}", flush=True)
        package(target, spec["environment"]["image"], final_env, labels, archive)
    finally:
        udocker.remove(name)

    store = Udocker(out / "udocker")
    for d in ("repos", "layers", "containers"):
        (store.store / d).mkdir(parents=True, exist_ok=True)
    if store.has_image(spec["environment"]["image"]):
        store.call("rmi", spec["environment"]["image"])
    store.call("load", "-i", str(archive))
    if validate:
        subprocess.run([sys.executable, str(HERE.parent / "validate.py"), "--store", str(store.store), task.id], check=True)


# ---------------------------------------------------------------- check

def check(task):
    """Fail unless every source of the task's recipe is reachable."""
    recipe, problems = RECIPES[task.id], []
    try:
        if "atlas" in recipe:
            layers = atlas_layers(ATLAS + recipe["atlas"])[2]
            print(f"{task.id}: Atlas image, {len(layers)} layers, {sum(l['size'] for l in layers) >> 20} MiB")
        else:
            src = task.spec["source"]
            refs = subprocess.run(["git", "ls-remote", src["repository"], "HEAD"], capture_output=True, text=True, timeout=120)
            problems += [] if refs.returncode == 0 else [f"git ls-remote {src['repository']} failed"]
            print(f"{task.id}: {src['repository']} reachable")
        if recipe.get("go"):
            releases = json.load(urllib.request.urlopen("https://go.dev/dl/?mode=json&include=all", timeout=60))
            if not any(r["version"] == "go" + recipe["go"] for r in releases):
                problems.append(f"go{recipe['go']} not listed on go.dev")
    except Exception as e:  # report every task, then fail
        problems.append(f"{type(e).__name__}: {e}")
    if not (data_dir(task) / "source").is_dir():
        problems.append("missing source/")
    for p in problems:
        print(f"{task.id}: PROBLEM {p}")
    return not problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tasks", nargs="*", help="task ids (default: all six image tasks)")
    parser.add_argument("--out", type=Path, default=Path("/tmp/cs408-lab2-images"), help="archives and image store")
    parser.add_argument("--work", type=Path, default=Path("/tmp/cs408-lab2-build"), help="build containers and downloads")
    parser.add_argument("--no-validate", action="store_true", help="skip construction/validate.py")
    parser.add_argument("--check", action="store_true", help="only check that the sources are reachable")
    args = parser.parse_args()
    ids = task_ids(args.tasks)
    if args.check:
        ok = all([check(tasks.load(i)) for i in ids]) and SEED.is_dir()
        print("seed container", "present" if SEED.is_dir() else "MISSING", SEED)
        raise SystemExit(0 if ok else 1)
    args.work.mkdir(parents=True, exist_ok=True)
    for task_id in ids:
        build(tasks.load(task_id), args.out.resolve(), args.work.resolve(), not args.no_validate)


if __name__ == "__main__":
    main()
