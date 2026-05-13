import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SETUP = ROOT / "setup"
LAUNCH_PAIR = ROOT / "scripts" / "launch-pair"
HARNESS = ROOT / "scripts" / "mingjie-harness"


class SetupScriptsTests(unittest.TestCase):
    def test_setup_dry_run_smoke(self):
        result = subprocess.run(
            [sys.executable, str(SETUP), "--dry-run"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("mingjie-stack setup", result.stdout)
        self.assertIn("Dry run complete", result.stdout)
        self.assertIn("harness", result.stdout)

    def test_setup_hooks_dry_run_is_opt_in(self):
        result = subprocess.run(
            [sys.executable, str(SETUP), "--dry-run", "--hooks"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("Hooks:", result.stdout)
        self.assertIn("--hooks", result.stdout)

    def test_launch_pair_help_documents_layout_option(self):
        result = subprocess.run(
            [str(LAUNCH_PAIR), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
        )

        self.assertIn("--layout 2", result.stdout)
        self.assertIn("--layout 3", result.stdout)

    def test_harness_help_documents_core_commands(self):
        result = subprocess.run(
            [sys.executable, str(HARNESS), "--help"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("init", result.stdout)
        self.assertIn("start-run", result.stdout)
        self.assertIn("append-evidence", result.stdout)


if __name__ == "__main__":
    unittest.main()
