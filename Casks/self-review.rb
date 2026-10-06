cask "self-review" do
  version "2.0.2"
  sha256 "6d7ee29a47cf92b46b078eb7c41c4fe9a77e8d0155bc3be8c9157e94bf7e2f45"

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
