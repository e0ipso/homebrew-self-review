cask "self-review" do
  version "1.37.1"
  sha256 "c7a64a01f0c937627d1d8a58fe5c625fb071cd89eb8ddab74ccaaa3f7109d542"

  url "https://github.com/e0ipso/self-review/releases/download/v#{version}/Self.Review-darwin-arm64-#{version}.zip"
  name "Self Review"
  desc "GitHub-style PR review UI for local git diffs"
  homepage "https://github.com/e0ipso/self-review"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on :macos
  depends_on arch: :arm64

  app "Self Review.app"
  binary "#{appdir}/Self Review.app/Contents/MacOS/Self Review", target: "self-review"

  # No zap stanza until generated and verified on a macOS host.
end
