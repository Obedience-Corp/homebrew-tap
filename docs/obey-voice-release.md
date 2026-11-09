# Obey Voice release procedure

Obey Voice uses prebuilt native archives from `Obedience-Corp/obey-voice`.
The formula supports macOS 15+ arm64 and Linux x86_64 with glibc 2.39+.
The upstream repository's `scripts/render_homebrew.py` generates the formula
only after verifying both public archives and their manifests.

1. Publish and verify the native release in the upstream repository. Generate
   `Formula/obey-voice.rb` from the downloaded public bytes and open a tap PR.
2. Let **Obey Voice bottles** pass on both native runners. It downloads the public
   archives, audits the formula, builds production bottles from the actual tap
   commit, tests a formula-revision upgrade and a bottle reinstall, then uninstalls.
   Synthetic settings, personas, sessions and model-cache files must survive.
   It does not download models or certify physical audio.
3. Download both `obey-voice-bottle-*` artifacts from the same successful run.
   Check each `evidence.json`, its tap commit and bottle SHA-256. Stage the bottles
   in a draft tap release named `obey-voice-vVERSION`. Use each bottle JSON's
   `filename` as the public upload name, not its `local_filename`.
4. Merge both JSON files with `brew bottle --merge --write --no-commit` in a
   disposable checkout of this tap. Copy the resulting formula into the PR.
   Preserve generated tags, cellars and checksums. Never substitute a bottle
   produced by the upstream private fixture tap.
5. Download the staged assets again and verify their hashes. Test the staged
   formula and bottles on supported hosts; record explicit model/provider setup,
   microphone permission handling, an audible response, interruption and session
   persistence. Physical audio evidence is separate from packaging CI.
6. Once those checks pass, publish the tap release, verify anonymous public
   downloads, then merge the PR. Verify the public install, upgrade and uninstall
   and retained user data. Never merge formula URLs pointing to a draft release.

The bottle-building workflow has read-only repository permissions and never
publishes. Publication is a separate owner-controlled step. Do not overwrite
published bottles or downgrade a newer formula. For a later rebuild of the same
upstream version, use Homebrew's revision/rebuild conventions and a distinct
release asset identity; the initial-release harness currently exercises revision 1.

`scripts/verify-obey-voice.py` installs into its host's Homebrew prefix. Run it
only on a disposable runner. It refuses an existing Obey Voice installation and
uses a fresh HOME for synthetic data, but it is not an isolation wrapper for a
developer's installed Homebrew.
