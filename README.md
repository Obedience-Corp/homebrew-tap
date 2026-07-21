# Obedience Corp Homebrew Tap

Homebrew packages for [Obedience Corp](https://github.com/Obedience-Corp) tools.

## Install

```bash
brew tap Obedience-Corp/tap
# Homebrew 6+: trust the org tap once
brew trust Obedience-Corp/tap
brew install agent-stream-dbg
```

### Packages

| Package | Type | Install |
|---------|------|---------|
| `agent-stream-dbg` | Formula (CLI/TUI) | `brew install agent-stream-dbg` |
| `festival` | Formula (CLI) | `brew install festival` |
| `festival` | Cask (app) | `brew install --cask festival` |
| `camp-graph` | Cask (app) | `brew install --cask camp-graph` |

## Formula vs Cask

| | **Formula** | **Cask** |
|--|-------------|----------|
| For | CLIs, libraries, daemons, TUIs | macOS GUI `.app` bundles |
| Install | `brew install name` | `brew install --cask name` |
| This repo | `Formula/agent-stream-dbg.rb`, `Formula/festival.rb` | `Casks/festival.rb`, `Casks/camp-graph.rb` |

**agent-stream-dbg** is a terminal tool → **Formula**, not Cask.

## Updating agent-stream-dbg

After a new GitHub release with platform assets
(`agent-stream-dbg_vX.Y.Z_<os>_<arch>.tar.gz`):

1. Bump `version`, asset URLs, and `sha256` in `Formula/agent-stream-dbg.rb`
2. Commit and push to this tap

## Links

- [agent-stream-dbg](https://github.com/Obedience-Corp/agent-stream-dbg)
- [festival](https://github.com/Obedience-Corp/festival)
