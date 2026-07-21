# Obedience Corp Homebrew Tap

Homebrew packages for [Obedience Corp](https://github.com/Obedience-Corp) tools.

## Install

```bash
brew tap Obedience-Corp/tap
brew install agent-stream-dbg
```

### Other packages

| Package | Type | Install |
|---------|------|---------|
| `agent-stream-dbg` | Formula (CLI) | `brew install agent-stream-dbg` |
| `festival` | Formula (CLI) | `brew install festival` |
| `festival` | Cask (app) | `brew install --cask festival` |
| `camp-graph` | Cask (app) | `brew install --cask camp-graph` |

## Formula vs Cask

| | **Formula** (this is a *tap* of formulas) | **Cask** |
|--|------------------------------------------|----------|
| For | CLIs, libraries, daemons | macOS GUI `.app` bundles |
| Examples | `agent-stream-dbg`, `fest`, `camp` | Festival.app, Camp Graph |
| Install | `brew install name` | `brew install --cask name` |

`agent-stream-dbg` is a terminal TUI — it belongs under **Formula/**, not Casks/.

## Updating agent-stream-dbg

After a new GitHub release with platform assets:

1. Update `version`, asset `url`s, and `sha256` values in `Formula/agent-stream-dbg.rb`
2. Commit and push to this tap

Asset naming from the main repo:

```text
agent-stream-dbg_vX.Y.Z_darwin_arm64.tar.gz
agent-stream-dbg_vX.Y.Z_darwin_amd64.tar.gz
agent-stream-dbg_vX.Y.Z_linux_amd64.tar.gz
agent-stream-dbg_vX.Y.Z_linux_arm64.tar.gz
```

## Links

- [agent-stream-dbg](https://github.com/Obedience-Corp/agent-stream-dbg)
- [festival](https://github.com/Obedience-Corp/festival)
