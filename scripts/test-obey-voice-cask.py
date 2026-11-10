import importlib.util
import json
from pathlib import Path
import plistlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("verify_cask", Path(__file__).with_name("verify-obey-voice-cask.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.bundle = Path(self.temp.name)
        (self.bundle / "Contents/Resources").mkdir(parents=True)
        info = dict(CFBundleIdentifier=verify.BUNDLE_ID, CFBundleShortVersionString="0.3.1",
                    CFBundleVersion="0.3.1", LSMinimumSystemVersion="15.0")
        (self.bundle / "Contents/Info.plist").write_bytes(plistlib.dumps(info))
        self.provenance = self.bundle / "Contents/Resources/release.json"
        self.metadata()

    def metadata(self, signing=None, preview=False):
        data = {"version": "v0.3.1", "source_sha": "a" * 40, "platform": "macos-arm64"}
        if signing:
            data.update(signing=signing, preview=preview)
        self.provenance.write_text(json.dumps(data))

    def test_installed_bundle_must_match_version_and_source(self):
        verify.identity(self.bundle, "0.3.1", "a" * 40)
        with self.assertRaisesRegex(ValueError, "source tag"):
            verify.identity(self.bundle, "0.3.1", "b" * 40)
        with self.assertRaisesRegex(ValueError, "identity/version"):
            verify.identity(self.bundle, "0.3.2", "a" * 40)

    def test_unversioned_cask_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "stable version"):
            verify.version('  version :latest')

    def test_preview_and_wrong_signing_provenance_rejected(self):
        self.metadata("ad-hoc", preview=True)
        with self.assertRaisesRegex(ValueError, "source tag"):
            verify.identity(self.bundle, "0.3.1", "a" * 40, "ad-hoc")
        self.metadata("ad-hoc")
        with self.assertRaisesRegex(ValueError, "source tag"):
            verify.identity(self.bundle, "0.3.1", "a" * 40, "notarized")

    def test_invalid_signing_policy_rejected(self):
        self.assertEqual(verify.signing_mode('cask "obey-voice-app" do'), "notarized")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            verify.signing_mode('# Signing mode: skip-checks')

    def adhoc(self, signature="Signature=adhoc", status=3, stderr="app: rejected", quarantine="0081;fixture"):
        self.metadata("ad-hoc")
        results = [subprocess.CompletedProcess([], 0, "", signature),
                   subprocess.CompletedProcess([], status, "", stderr)]
        with patch.object(verify, "command", side_effect=["", quarantine]) as command, \
                patch.object(verify.subprocess, "run", side_effect=results):
            evidence = verify.verify(self.bundle, "0.3.1", "a" * 40, {}, "ad-hoc")
        self.assertEqual([call.args[0] for call in command.call_args_list], ["codesign", "xattr"])
        return evidence

    def test_ad_hoc_retains_quarantine_and_reports_required_approval(self):
        evidence = self.adhoc()
        self.assertTrue(evidence["signature_verified"])
        self.assertTrue(evidence["gatekeeper_approval_required"])
        self.assertFalse(evidence["gatekeeper_accepted"])
        self.assertFalse(evidence["engine_startup_checked"])

    def test_ad_hoc_checks_do_not_silently_accept_gatekeeper_errors_or_bypass(self):
        for status, message in ((0, "accepted"), (1, "service failed"), (3, "unknown error")):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "unexpected Gatekeeper"):
                self.adhoc(status=status, stderr=message)
        with self.assertRaisesRegex(ValueError, "quarantine"):
            self.adhoc(quarantine="")

    def test_ad_hoc_requires_actual_ad_hoc_signature(self):
        with self.assertRaisesRegex(ValueError, "not ad-hoc signed"):
            self.adhoc(signature="Authority=Developer ID Application: Example")

    def test_notarized_mode_keeps_staple_gatekeeper_and_engine_checks(self):
        self.metadata("notarized")
        signature = subprocess.CompletedProcess([], 0, "", "Authority=Developer ID Application: Example\nflags=runtime")
        with patch.object(verify.subprocess, "run", return_value=signature), \
                patch.object(verify, "command", side_effect=["", "", "", "obey-voice v0.3.1"]) as command:
            evidence = verify.verify(self.bundle, "0.3.1", "a" * 40, {})
        self.assertTrue(evidence["gatekeeper_accepted"])
        self.assertTrue(evidence["engine_startup_checked"])
        self.assertEqual([call.args[0] for call in command.call_args_list[:3]], ["codesign", "xcrun", "spctl"])

    def test_corrupt_signature_blocks_verification(self):
        self.metadata("ad-hoc")
        with patch.object(verify, "command", side_effect=RuntimeError("invalid signature")):
            with self.assertRaisesRegex(RuntimeError, "invalid signature"):
                verify.verify(self.bundle, "0.3.1", "a" * 40, {}, "ad-hoc")


if __name__ == "__main__":
    unittest.main()
