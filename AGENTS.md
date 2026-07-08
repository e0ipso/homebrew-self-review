# Repository Guide

This repository is the `e0ipso/self-review` Homebrew tap for the Self Review
desktop app. It does not contain the app source code; it contains package
definitions and automation for installing release artifacts from
`e0ipso/self-review`.

## Project Layout

- `Casks/self-review.rb`: macOS Apple Silicon cask for the `.app` ZIP.
- `Formula/self-review.rb`: Linux x64 formula for the Electron ZIP.
- `.github/workflows/tests.yml`: CI checks for audit, style, install, version,
  and formula test coverage.
- `.github/workflows/update-homebrew-tap.yml`: release-driven updater for the
  version and SHA-256 values in the cask and formula.
- `.github/workflows/publish.yml`: Homebrew `brew pr-pull` helper workflow from
  the generated tap skeleton.

## Validation

Use Homebrew tap names for audit and style commands; recent Homebrew versions
reject path-based audit commands.

```bash
brew tap e0ipso/self-review "$PWD"
brew audit --cask --strict e0ipso/self-review/self-review
brew style --cask e0ipso/self-review/self-review
brew audit --formula --strict e0ipso/self-review/self-review
brew style --formula e0ipso/self-review/self-review
```

For a full local smoke test, also run:

```bash
brew install --cask --verbose e0ipso/self-review/self-review
self-review --version
brew uninstall --cask self-review

brew install --verbose e0ipso/self-review/self-review
self-review --version
brew test self-review
brew uninstall self-review
```

## Release Updates

When updating manually, use the asset digests from the matching upstream GitHub
release:

- `Self.Review-darwin-arm64-<version>.zip` updates the cask `version` and
  `sha256`.
- `Self.Review-linux-x64-<version>.zip` updates the formula `url` and `sha256`.

Keep platform notes accurate: macOS is Apple Silicon only until an Intel macOS
ZIP exists, and Linux Homebrew is x64 only until a Linux ARM64 ZIP exists.
