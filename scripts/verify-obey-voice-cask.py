#!/usr/bin/env python3
"""Verify public desktop downloads through Homebrew on a disposable macOS runner."""

import argparse
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
from urllib.request import urlopen


TOKEN = "obedience-corp/tap/obey-voice-app"
APP = "Obey Voice Agent.app"
BUNDLE_ID = "com.obedience.voice-agent"


def command(*args, env=None):
    result = subprocess.run(args, env=env, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError(f"{args[0]} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def version(text):
    match = re.search(r'^  version "([0-9]+\.[0-9]+\.[0-9]+)"$', text, re.M)
    if not match:
        raise ValueError("cask must have a stable version")
    return match[1]


def identity(bundle, expected, source):
    info = plistlib.loads((bundle / "Contents/Info.plist").read_bytes())
    if (info.get("CFBundleIdentifier"), info.get("CFBundleShortVersionString"),
            info.get("CFBundleVersion"), info.get("LSMinimumSystemVersion")) != (BUNDLE_ID, expected, expected, "15.0"):
        raise ValueError("installed app identity/version/platform mismatch")
    provenance = json.loads((bundle / "Contents/Resources/release.json").read_text())
    if provenance != {"version": "v" + expected, "source_sha": source, "platform": "macos-arm64"}:
        raise ValueError("installed app does not match its public source tag")


def verify(bundle, expected, source, env):
    identity(bundle, expected, source)
    command("codesign", "--verify", "--deep", "--strict", str(bundle))
    signature = subprocess.run(["codesign", "-dv", "--verbose=4", str(bundle)],
                               capture_output=True, text=True, check=True).stderr
    if "Authority=Developer ID Application:" not in signature or "runtime" not in signature:
        raise ValueError("desktop app is not signed with Developer ID and hardened runtime")
    command("xcrun", "stapler", "validate", str(bundle))
    command("spctl", "--assess", "--type", "execute", "--verbose=2", str(bundle))
    engine = bundle / "Contents/MacOS/obey-voice-engine"
    if "v" + expected not in command(str(engine), "--version", env=env).split():
        raise ValueError("installed desktop engine has wrong version")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("verify", "public"), required=True)
    args = parser.parse_args()
    # Caskroom is shared by a Homebrew installation. Never run lifecycle tests
    # against someone's normal machine; hosted runners are disposable.
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise ValueError("cask lifecycle checks require a disposable GitHub Actions runner")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    home, apps = output / "home", output / "Applications"
    home.mkdir()
    apps.mkdir()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("DYLD_", "LD_", "OBEY_", "SAMANTHA_"))}
    env.update(HOME=str(home), HOMEBREW_NO_AUTO_UPDATE="1", HOMEBREW_NO_ANALYTICS="1",
               XDG_CONFIG_HOME=str(home / ".config"), XDG_CACHE_HOME=str(home / ".cache"))
    command("brew", "trust", "--tap", "obedience-corp/tap", env=env)
    if command("brew", "list", "--cask", env=env).split():
        # Only this token matters; unrelated runner casks are not touched.
        if "obey-voice-app" in command("brew", "list", "--cask", env=env).split():
            raise ValueError("runner already has Obey Voice installed")
    tap = Path(command("brew", "--repository", "obedience-corp/tap", env=env))
    cask = tap / "Casks/obey-voice-app.rb"
    desired = cask.read_text()
    expected = version(desired)
    with urlopen(f"https://api.github.com/repos/Obedience-Corp/obey-voice/commits/v{expected}", timeout=60) as response:
        source = json.load(response)["sha"]
    fixtures = [home / ".obey/agents/voice/obey-voice/cask-fixture.json", home / ".cache/obey-voice/cask-fixture"]
    for path in fixtures:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("preserve user data\n")
    evidence = {"version": expected, "source_sha": source,
                "tap_commit": command("git", "-C", str(tap), "rev-parse", "HEAD"), "mode": args.mode}
    try:
        command("brew", "style", "--cask", TOKEN, env=env)
        command("brew", "audit", "--cask", "--strict", TOKEN, env=env)
        previous = subprocess.run(["git", "-C", str(tap), "show", "origin/main:Casks/obey-voice-app.rb"],
                                  capture_output=True, text=True)
        old = previous.stdout if previous.returncode == 0 else None
        if old and version(old) != expected:
            cask.write_text(old)
            command("brew", "install", "--cask", f"--appdir={apps}", TOKEN, env=env)
            cask.write_text(desired)
            command("brew", "upgrade", "--cask", f"--appdir={apps}", TOKEN, env=env)
            evidence["upgraded_from"] = version(old)
        else:
            command("brew", "install", "--cask", f"--appdir={apps}", TOKEN, env=env)
            evidence["upgraded_from"] = None
        verify(apps / APP, expected, source, env)
        evidence["installed_and_gatekeeper_accepted"] = True
        command("brew", "reinstall", "--cask", f"--appdir={apps}", TOKEN, env=env)
        verify(apps / APP, expected, source, env)
        evidence["reinstalled"] = True
        command("brew", "uninstall", "--cask", TOKEN, env=env)
        if (apps / APP).exists():
            raise ValueError("uninstall left the app installed")
        if any(path.read_text() != "preserve user data\n" for path in fixtures):
            raise ValueError("cask lifecycle changed user data")
        evidence.update(uninstalled=True, user_data_preserved=True)
    finally:
        cask.write_text(desired)
        (output / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")


if __name__ == "__main__":
    main()
