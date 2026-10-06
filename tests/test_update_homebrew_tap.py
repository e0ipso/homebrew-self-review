"""Exercise the updater's shell steps without contacting GitHub or Homebrew."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/update-homebrew-tap.yml").read_text()
)
STEPS = WORKFLOW["jobs"]["update"]["steps"]
RESOLVE = next(step["run"] for step in STEPS if step.get("id") == "release")
DARWIN_SHA = "a" * 64
LINUX_SHA = "b" * 64


def release(version, **overrides):
    return {
        "tag_name": f"v{version}",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": f"Self.Review-{platform}-{version}.zip",
                "digest": f"sha256:{digest}",
            }
            for platform, digest in (
                ("darwin-arm64", DARWIN_SHA), ("linux-x64", LINUX_SHA)
            )
        ],
        **overrides,
    }


class UpdateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        for directory in ("Casks", "Formula"):
            shutil.copytree(ROOT / directory, self.workspace / directory)
        subprocess.run(
            ["git", "init", "-q"], cwd=self.workspace, check=True
        )
        self.bin = self.workspace / "mock-bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(
            f"#!{sys.executable}\n" + '''
import json
import os
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

if os.environ.get("API_FAILURE"):
    sys.exit(1)
args = sys.argv[1:]
endpoint = next(arg for arg in args if arg.startswith("repos/"))
releases = json.loads(open("releases.json").read())
if "/tags/" in endpoint:
    tag = endpoint.rsplit("/", 1)[1]
    pages = [next(r for r in releases if r["tag_name"] == tag)]
else:
    size = int(parse_qs(urlparse(endpoint).query).get("per_page", [30])[0])
    pages = [releases[i:i + size] for i in range(0, len(releases), size)] or [[]]
    if "--paginate" not in args:
        pages = pages[:1]
query = args[args.index("--jq") + 1]
for page in pages:
    result = subprocess.run(
        ["jq", "-r", query], input=json.dumps(page), text=True, check=True,
        capture_output=True,
    )
    print(result.stdout, end="")
'''
        )
        gh.chmod(0o755)
        sleep = self.bin / "sleep"
        sleep.write_text("#!/bin/sh\nexit 0\n")
        sleep.chmod(0o755)
        self.output = self.workspace / "output"
        self.env = {
            **os.environ,
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "APP_REPOSITORY": "e0ipso/self-review",
            "GITHUB_OUTPUT": str(self.output),
            "GIT_CONFIG_GLOBAL": str(self.workspace / "global.gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "REQUESTED_TAG": "",
        }

    def resolve(self, releases, current="1.44.0", tag="", **environment):
        (self.workspace / "releases.json").write_text(json.dumps(releases))
        (self.workspace / "Casks/self-review.rb").write_text(
            f'cask "self-review" do\n  version "{current}"\nend\n'
        )
        result = subprocess.run(
            ["bash", "-c", RESOLVE], cwd=self.workspace,
            env={**self.env, "REQUESTED_TAG": tag, **environment},
            text=True, capture_output=True, timeout=30,
        )
        outputs = dict(
            line.split("=", 1) for line in self.output.read_text().splitlines()
        ) if self.output.exists() else {}
        return result, outputs

    def test_selects_highest_complete_stable_version(self):
        releases = [
            release("3.0.0", prerelease=True),
            release("4.0.0", draft=True),
            release("5.0.0", assets=[]),
            release("6.0.0", assets=[
                {"name": "Self.Review-darwin-arm64-6.0.0.zip", "digest": None}
            ]),
            release("2.1.0"), release("2.9.0"), release("2.10.0"),
        ]
        result, outputs = self.resolve(releases)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs, {
            "skip": "false", "tag": "v2.10.0", "version": "2.10.0",
            "darwin_sha": DARWIN_SHA, "linux_sha": LINUX_SHA,
        })

    def test_finds_complete_release_on_later_pages(self):
        releases = [release(f"3.0.{i}", assets=[]) for i in range(101)]
        result, outputs = self.resolve(releases + [release("2.0.2")])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("version"), "2.0.2")

    def test_poll_does_not_repeat_or_downgrade_updates(self):
        for current in ("2.0.2", "2.0.3"):
            with self.subTest(current=current):
                result, outputs = self.resolve([release("2.0.2")], current=current)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(outputs, {"skip": "true"})

    def test_skips_when_no_release_has_both_assets(self):
        result, outputs = self.resolve([release("2.0.2", assets=[])])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs, {"skip": "true"})

    def test_explicit_tag_selects_requested_release(self):
        result, outputs = self.resolve(
            [release("2.0.2"), release("2.1.0")], tag="v2.0.2"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(outputs.get("version"), "2.0.2")

    def test_invalid_requested_tag_fails(self):
        result, outputs = self.resolve([], tag="v2.0.2; touch unexpected")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs, {})

    def test_api_failure_is_not_reported_as_no_updates(self):
        result, outputs = self.resolve([], API_FAILURE="1")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outputs, {})

    def test_package_changes_survive_homebrew_setup(self):
        originals = {
            path: (self.workspace / path).read_text()
            for path in ("Casks/self-review.rb", "Formula/self-review.rb")
        }
        env = {
            **self.env, "VERSION": "2.0.2",
            "DARWIN_SHA256": DARWIN_SHA, "LINUX_SHA256": LINUX_SHA,
        }
        auth_key = "http.https://github.com/.extraheader"

        def git_config(*args, check=True):
            return subprocess.run(
                ["git", "config", *args], cwd=self.workspace, env=env,
                check=check, text=True, capture_output=True,
            )

        for step in STEPS:
            if step.get("uses", "").startswith("actions/checkout@"):
                if step.get("with", {}).get("token"):
                    git_config("--local", auth_key, "Authorization: basic CHECKOUT")
            elif step.get("uses", "").startswith("Homebrew/actions/setup-homebrew@"):
                # On hosted runners this action replaces the entire checkout,
                # discarding both local file edits and checkout's credentials.
                for path, contents in originals.items():
                    (self.workspace / path).write_text(contents)
                git_config("--local", "--unset-all", auth_key, check=False)
                if step.get("with", {}).get("token"):
                    git_config("--global", auth_key, "Authorization: basic SETUP")
            elif step.get("name") == "Update package definitions":
                result = subprocess.run(
                    ["bash", "-c", step["run"]], cwd=self.workspace, env=env,
                    text=True, capture_output=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
        headers = git_config("--get-all", auth_key, check=False).stdout.splitlines()
        self.assertEqual(headers, ["Authorization: basic CHECKOUT"],
                         "Push must use exactly the restored checkout credentials")
        cask = (self.workspace / "Casks/self-review.rb").read_text()
        formula = (self.workspace / "Formula/self-review.rb").read_text()
        self.assertIn('version "2.0.2"', cask)
        self.assertIn(DARWIN_SHA, cask)
        self.assertIn("/v2.0.2/Self.Review-linux-x64-2.0.2.zip", formula)
        self.assertIn(LINUX_SHA, formula)


if __name__ == "__main__":
    unittest.main()
