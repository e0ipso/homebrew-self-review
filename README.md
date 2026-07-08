# E0ipso Self Review Homebrew Tap

This repository is the Homebrew tap for
[Self Review](https://github.com/e0ipso/self-review), a desktop app that gives
local git diffs a GitHub-style pull request review interface.

The tap publishes:

- A macOS cask for the Apple Silicon `.app` ZIP.
- A Linux formula for the x64 Electron ZIP.
- GitHub Actions checks that audit, style, install, and smoke-test both package
  definitions.
- An update workflow that bumps the cask and formula after upstream releases.

## Install

macOS:

```bash
brew install --cask e0ipso/self-review/self-review
```

Linux:

```bash
brew install e0ipso/self-review/self-review
```

Or tap the repository first:

```bash
brew tap e0ipso/self-review
brew install --cask self-review # macOS
brew install self-review        # Linux
```

In a `Brewfile`:

```ruby
tap "e0ipso/self-review"
cask "self-review" # macOS
brew "self-review" # Linux
```

## Platform Limits

- macOS Homebrew install is Apple Silicon only until an Intel macOS ZIP exists.
- Linux Homebrew install is x64 only until a Linux ARM64 ZIP exists.
- macOS Gatekeeper/quarantine warnings may appear until the app is signed and notarized.

## Manual Fallbacks

If Homebrew is not available for your platform yet, download the release assets directly from
[e0ipso/self-review releases](https://github.com/e0ipso/self-review/releases):

- macOS: `Self.Review-darwin-arm64-<version>.zip`
- Linux ZIP: `Self.Review-linux-x64-<version>.zip`
- Debian/Ubuntu: `self-review_<version>_amd64.deb`
- Fedora/RHEL-compatible: `self-review-<version>-1.x86_64.rpm`

## Maintaining This Tap

Package definitions live in [`Casks/self-review.rb`](Casks/self-review.rb) and
[`Formula/self-review.rb`](Formula/self-review.rb). Both point at release assets
from `e0ipso/self-review` and use the SHA-256 digests published with each
GitHub release.

To validate changes locally:

```bash
brew tap e0ipso/self-review "$PWD"
brew audit --cask --strict e0ipso/self-review/self-review
brew style --cask e0ipso/self-review/self-review
brew audit --formula --strict e0ipso/self-review/self-review
brew style --formula e0ipso/self-review/self-review
```

The `update homebrew tap` workflow accepts a release tag such as `v1.38.0`,
waits for the macOS and Linux ZIP assets, updates the cask/formula versions and
checksums, runs tap checks, and commits the result.

## Homebrew Documentation

`brew help`, `man brew` or check [Homebrew's documentation](https://docs.brew.sh).
