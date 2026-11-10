#!/usr/bin/env python3
"""Exercise ad-hoc cask installs using a tiny app on disposable hosted runners."""

import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import os
from pathlib import Path
import plistlib
import subprocess
import tempfile
import threading

spec = importlib.util.spec_from_file_location("verify_cask", Path(__file__).with_name("verify-obey-voice-cask.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true":
        raise ValueError("fixture requires a disposable GitHub Actions runner")
    with tempfile.TemporaryDirectory(prefix="obey-cask-fixture-") as scratch:
        root = Path(scratch)
        apps, home = root / "Applications", root / "home"
        apps.mkdir()
        home.mkdir()
        env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"),
                   XDG_CACHE_HOME=str(home / ".cache"), HOMEBREW_NO_AUTO_UPDATE="1", HOMEBREW_NO_ANALYTICS="1")
        def command(*args):
            return verify.command(*args, env=env)
        command("brew", "trust", "--tap", "obedience-corp/tap")
        if "obey-voice-app" in command("brew", "list", "--cask").split():
            raise ValueError("fixture must not replace an installed app")
        tap = Path(command("brew", "--repository", "obedience-corp/tap"))
        cask = tap / "Casks/obey-voice-app.rb"
        original = cask.read_bytes() if cask.exists() else None
        source = "a" * 40
        bundle = root / verify.APP
        (bundle / "Contents/MacOS").mkdir(parents=True)
        (bundle / "Contents/Resources").mkdir()
        c_source = root / "fixture.c"
        c_source.write_text('int main(void) { return 0; }\n')
        command("clang", "-arch", "arm64", str(c_source), "-o", str(bundle / "Contents/MacOS/obey-voice-agent"))
        settings = home / ".config/obey-voice-fixture"
        settings.parent.mkdir()
        settings.write_text("preserve settings\n")
        handler = functools.partial(SimpleHTTPRequestHandler, directory=str(root))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        installed = False
        try:
            for version, action in (("0.0.1", "install"), ("0.0.2", "upgrade")):
                info = dict(CFBundleIdentifier=verify.BUNDLE_ID, CFBundleName="Obey Voice Agent",
                            CFBundleExecutable="obey-voice-agent", CFBundlePackageType="APPL",
                            CFBundleShortVersionString=version, CFBundleVersion=version,
                            LSMinimumSystemVersion="15.0")
                (bundle / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
                (bundle / "Contents/Resources/release.json").write_text(json.dumps({
                    "version": "v" + version, "source_sha": source, "platform": "macos-arm64",
                    "signing": "ad-hoc", "preview": False}))
                command("codesign", "--force", "--sign", "-", str(bundle))
                archive = root / f"fixture-{version}.zip"
                command("ditto", "-c", "-k", "--keepParent", str(bundle), str(archive))
                checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
                cask.write_text(f'''# Signing mode: ad-hoc
cask "obey-voice-app" do
  version "{version}"
  sha256 "{checksum}"
  url "http://127.0.0.1:{server.server_port}/fixture-#{{version}}.zip"
  name "Obey Voice Agent"
  desc "Disposable ad-hoc cask fixture"
  homepage "https://github.com/Obedience-Corp/obey-voice"
  depends_on arch: :arm64
  depends_on macos: :sequoia
  app "Obey Voice Agent.app"
end
''')
                command("brew", action, "--cask", f"--appdir={apps}", verify.TOKEN)
                installed = True
                evidence = verify.verify(apps / verify.APP, version, source, env, "ad-hoc")
                assert evidence["gatekeeper_approval_required"] and not evidence["gatekeeper_accepted"]
            command("brew", "reinstall", "--cask", f"--appdir={apps}", verify.TOKEN)
            verify.verify(apps / verify.APP, "0.0.2", source, env, "ad-hoc")
            command("brew", "uninstall", "--cask", verify.TOKEN)
            installed = False
            assert not (apps / verify.APP).exists()
            assert settings.read_text() == "preserve settings\n"
            print("Ad-hoc fixture: install, upgrade, reinstall, uninstall, quarantine, signature and Gatekeeper checks passed.")
        finally:
            if installed:
                subprocess.run(["brew", "uninstall", "--cask", verify.TOKEN], env=env, check=False)
            if original is None:
                cask.unlink(missing_ok=True)
            else:
                cask.write_bytes(original)
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
