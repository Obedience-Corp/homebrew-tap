#!/usr/bin/env python3
"""Build an Obey Voice bottle from the installed tap revision on a disposable host.

Run only on a disposable runner: this installs and uninstalls the formula in the
runner's Homebrew prefix. User fixtures and caches use a fresh isolated HOME.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


FORMULA = "obedience-corp/tap/obey-voice"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, HOME=str(output / "user"),
               HOMEBREW_CACHE=str(output / "cache"),
               HOMEBREW_NO_AUTO_UPDATE="1", HOMEBREW_NO_ANALYTICS="1",
               HOMEBREW_NO_INSTALL_CLEANUP="1", HOMEBREW_NO_ASK="1")
    Path(env["HOME"]).mkdir()
    env.pop("XDG_CONFIG_HOME", None)
    env.pop("XDG_CACHE_HOME", None)

    def run(*args, cwd=output):
        command = [str(arg) for arg in args]
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=cwd, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=1200)
        with (output / "verification.log").open("a") as log:
            log.write("+ " + " ".join(command) + "\n" + result.stdout)
        if result.returncode:
            print(result.stdout, flush=True)
            raise subprocess.CalledProcessError(result.returncode, command)
        return result.stdout.strip()

    installed = json.loads(run("brew", "info", "--json=v2", FORMULA))["formulae"][0]
    if installed["installed"]:
        raise ValueError("refusing to replace an installed Obey Voice; use a disposable runner")
    tap = Path(run("brew", "--repository", "obedience-corp/tap"))
    source_commit = run("git", "rev-parse", "HEAD", cwd=tap)
    formula = tap / "Formula/obey-voice.rb"
    original = formula.read_text()
    version = installed["versions"]["stable"]
    roots = [Path(env["HOME"]) / ".obey/agents/voice/obey-voice",
             Path(env["HOME"]) / ".cache/obey-voice"]
    for root, relative in [(roots[0], "config.yaml"), (roots[0], "personas/fixture.yaml"),
                           (roots[0], "sessions/fixture.json"), (roots[1], "models/fixture.bin")]:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("preserve this synthetic user fixture\n")

    def snapshot():
        return {str(path.relative_to(Path(env["HOME"]))): digest(path)
                for root in roots for path in root.rglob("*") if path.is_file()}

    protected = snapshot()

    def preserved():
        if snapshot() != protected:
            raise ValueError("user data changed or model files were added")

    run("brew", "trust", "--tap", "obedience-corp/tap")
    run("brew", "audit", "--strict", "--formula", FORMULA)
    # Fetch real public native assets; no upstream cache is seeded.
    run("brew", "install", "--build-bottle", "--formula", FORMULA)
    run("brew", "test", FORMULA)
    preserved()
    bottles = output / "bottles"
    bottles.mkdir()
    run("brew", "bottle", "--json", "--no-rebuild", "--root-url",
        "https://github.com/Obedience-Corp/homebrew-tap/releases/download/obey-voice-v" + version,
        FORMULA, cwd=bottles)
    metadata, = bottles.glob("*.bottle.json")
    bottle, = bottles.glob("*.bottle.tar.gz")
    # Exercise a packaging revision upgrade without claiming application migration.
    formula.write_text(original.replace('  license "AGPL-3.0-only"',
                                        '  revision 1\n  license "AGPL-3.0-only"'))
    run("brew", "upgrade", "--formula", FORMULA)
    run("brew", "test", FORMULA)
    preserved()
    run("brew", "uninstall", "--force", "--formula", FORMULA)
    formula.write_text(original)
    run("brew", "bottle", "--merge", "--write", "--no-commit", metadata)
    cached = Path(run("brew", "--cache", "--force-bottle", "--formula", FORMULA))
    cached.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(bottle, cached)
    run("brew", "install", "--force-bottle", "--formula", FORMULA)
    run("brew", "test", FORMULA)
    prefix = Path(run("brew", "--prefix", FORMULA))
    receipt = json.loads((prefix / "INSTALL_RECEIPT.json").read_text())
    if not receipt.get("poured_from_bottle"):
        raise ValueError("installation did not pour the production bottle")
    preserved()
    run("brew", "uninstall", "--force", "--formula", FORMULA)
    preserved()
    executable = Path(run("brew", "--prefix")) / "bin/obey-voice"
    if prefix.exists() or executable.exists() or executable.is_symlink():
        raise ValueError("uninstall left package-owned files")
    formula.write_text(original)
    evidence = {"version": version, "tap_commit": source_commit,
                "bottle": bottle.name, "sha256": digest(bottle),
                "public_native_download": True, "poured_from_bottle": True,
                "revision_upgrade": True, "user_data_preserved": True, "uninstalled": True}
    (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))
    # Only evidence and synthetic data are uploaded, not caches or the user's HOME.
    shutil.rmtree(output / "cache", ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    verify(parser.parse_args().output)
