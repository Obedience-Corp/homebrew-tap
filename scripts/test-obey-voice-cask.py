import importlib.util
import json
from pathlib import Path
import plistlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("verify_cask", Path(__file__).with_name("verify-obey-voice-cask.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class IdentityTests(unittest.TestCase):
    def test_installed_bundle_must_match_version_and_source(self):
        with tempfile.TemporaryDirectory() as scratch:
            bundle = Path(scratch)
            (bundle / "Contents/Resources").mkdir(parents=True)
            info = dict(CFBundleIdentifier=verify.BUNDLE_ID, CFBundleShortVersionString="0.3.1",
                        CFBundleVersion="0.3.1", LSMinimumSystemVersion="15.0")
            (bundle / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
            (bundle / "Contents/Resources/release.json").write_text(json.dumps(
                {"version": "v0.3.1", "source_sha": "a" * 40, "platform": "macos-arm64"}))
            verify.identity(bundle, "0.3.1", "a" * 40)
            with self.assertRaisesRegex(ValueError, "source tag"):
                verify.identity(bundle, "0.3.1", "b" * 40)
            with self.assertRaisesRegex(ValueError, "identity/version"):
                verify.identity(bundle, "0.3.2", "a" * 40)

    def test_unversioned_cask_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "stable version"):
            verify.version('  version :latest')


if __name__ == "__main__":
    unittest.main()
