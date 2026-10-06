class SelfReview < Formula
  desc "GitHub-style PR review UI for local git diffs"
  homepage "https://github.com/e0ipso/self-review"
  url "https://github.com/e0ipso/self-review/releases/download/v1.44.0/Self.Review-linux-x64-1.44.0.zip"
  sha256 "80da1ced561289a4cb8f18be82351794c6f3cb6802a945d11b25994e64e2c8c8"
  license "MIT"

  depends_on "patchelf" => :build
  depends_on "alsa-lib"
  depends_on "cups"
  depends_on "dbus"
  depends_on "glibc"
  depends_on "gtk+3"
  depends_on "libxcomposite"
  depends_on "libxdamage"
  depends_on "libxfixes"
  depends_on "libxkbcommon"
  depends_on "libxrandr"
  depends_on :linux
  depends_on "mesa"
  depends_on "nss"

  def install
    source_dir = Dir.exist?("Self Review-linux-x64") ? "Self Review-linux-x64" : "."
    library_paths = [
      formula_opt_lib("glibc"),
      HOMEBREW_PREFIX/"lib",
      formula_opt_lib("cups"),
      "/lib/x86_64-linux-gnu",
      "/usr/lib/x86_64-linux-gnu",
      "/lib64",
      "/usr/lib64",
    ].join(":")
    rpath = ["$ORIGIN", library_paths].join(":")

    libexec.install Dir["#{source_dir}/*"]
    system formula_opt_lib("glibc")/"ld-linux-x86-64.so.2",
           "--library-path", library_paths,
           formula_opt_bin("patchelf")/"patchelf",
           "--set-interpreter", formula_opt_lib("glibc")/"ld-linux-x86-64.so.2",
           "--set-rpath", rpath,
           libexec/"self-review"

    (bin/"self-review").write <<~EOS
      #!/bin/sh
      export ELECTRON_DISABLE_SANDBOX="${ELECTRON_DISABLE_SANDBOX:-1}"
      export LD_LIBRARY_PATH="#{library_paths}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
      cd "#{libexec}"
      exec ./self-review "$@"
    EOS
    chmod 0755, bin/"self-review"
  end

  test do
    assert_match "self-review v#{version}", shell_output("#{bin}/self-review --version 2>&1")
  end
end
