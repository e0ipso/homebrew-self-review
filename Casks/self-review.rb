cask "self-review" do
  version "2.1.4"
  sha256 "2b9430adeeff6a7e43a745e2b31d0f46174bde41c95f9862f0345900d0961a4d"

  url "https://github.com/e0ipso/self-review/releases/download/v#{version}/Self.Review-darwin-arm64-#{version}.zip"
  name "Self Review"
  desc "GitHub-style PR review UI for local git diffs"
  homepage "https://github.com/e0ipso/self-review"

  livecheck do
    url :url
    strategy :github_latest
  end

  depends_on arch: :arm64
  depends_on :macos

  app "Self Review.app"
  # Electron must launch from the bundle path to find its helper apps.
  command_wrapper "self-review",
                  executable: "#{appdir}/Self Review.app/Contents/MacOS/Self Review"

  # No zap stanza until generated and verified on a macOS host.
end
