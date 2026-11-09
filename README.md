# Obedience Corp Homebrew Tap

Homebrew packages for [Obedience Corp](https://github.com/Obedience-Corp) tools.

## Install

```bash
brew tap Obedience-Corp/tap
# Homebrew 6+: trust the org tap once
brew trust Obedience-Corp/tap
brew install agent-stream-dbg
brew install gaze
```

### Packages

| Package | Type | Install |
|---------|------|---------|
| `gaze` | Formula (CLI) | `brew install gaze` (macOS and Linux) |
| `agent-stream-dbg` | Formula (CLI/TUI) | `brew install agent-stream-dbg` |
| `obey-voice` | Formula (CLI) | `brew install obedience-corp/tap/obey-voice` (macOS 15+ arm64; Linux x86_64, glibc 2.39+) |
| `festival` | Cask (fest, camp, festival CLIs) | `brew install --cask obedience-corp/tap/festival` |
| `camp-graph` | Cask (app) | `brew install --cask camp-graph` |

## Formula vs Cask

Obey Voice bundles its native speech libraries. Install a brain provider and
download speech models explicitly after installation; Homebrew does not start
services or download models. For the compiler-free speech path, select Parakeet
STT and Kokoro TTS. Settings, personas, sessions and model caches survive
uninstall. The Samantha package in the personal tap remains independent.
See the [Obey Voice release procedure](docs/obey-voice-release.md) for maintainers.

| | **Formula** | **Cask** |
|--|-------------|----------|
| For | CLIs, libraries, daemons, TUIs | macOS GUI `.app` bundles |
| Install | `brew install name` | `brew install --cask name` |
| This repo | `Formula/agent-stream-dbg.rb` | `Casks/festival.rb`, `Casks/camp-graph.rb` |

**agent-stream-dbg** is a terminal tool → **Formula**, not Cask.

## Updating agent-stream-dbg

After a new GitHub release with platform assets
(`agent-stream-dbg_vX.Y.Z_<os>_<arch>.tar.gz`):

1. Bump `version`, asset URLs, and `sha256` in `Formula/agent-stream-dbg.rb`
2. Commit and push to this tap

## Links

- [gaze](https://github.com/Obedience-Corp/gaze)
- [agent-stream-dbg](https://github.com/Obedience-Corp/agent-stream-dbg)
- [festival](https://github.com/Obedience-Corp/festival)
