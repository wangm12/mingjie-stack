import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "mingjie-harness"


class HarnessCliTests(unittest.TestCase):
    def run_harness(self, *args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HARNESS), *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_init_creates_docs_harness_and_gitignore_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / ".gitignore").write_text("*.pyc\n", encoding="utf-8")

            result = self.run_harness("init", cwd=project)

            self.assertIn("docs/mingjie-stack", result.stdout)
            self.assertTrue((project / "docs" / "mingjie-stack" / "PROJECT.md").exists())
            self.assertTrue((project / "docs" / "mingjie-stack" / "RUNBOOK.md").exists())
            gitignore = (project / ".gitignore").read_text(encoding="utf-8")
            self.assertIn("docs/mingjie-stack/STATE.md", gitignore)
            self.assertIn("docs/mingjie-stack/runs/", gitignore)

    def test_run_state_and_evidence_use_docs_harness_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)

            self.run_harness("start-run", "--id", "run-1", cwd=project)
            self.run_harness(
                "update-state",
                "--run-id",
                "run-1",
                "--stage",
                "build",
                "--next",
                "review",
                cwd=project,
            )
            self.run_harness(
                "append-evidence",
                "--run-id",
                "run-1",
                "--title",
                "unit tests",
                "--command",
                "python3 -m unittest discover tests",
                "--result",
                "OK",
                cwd=project,
            )

            state = (project / "docs" / "mingjie-stack" / "STATE.md").read_text(encoding="utf-8")
            evidence = (
                project
                / "docs"
                / "mingjie-stack"
                / "runs"
                / "run-1"
                / "EVIDENCE.md"
            ).read_text(encoding="utf-8")

            self.assertIn("run_id: run-1", state)
            self.assertIn("current_stage: build", state)
            self.assertIn("next_stage: review", state)
            self.assertIn("python3 -m unittest discover tests", evidence)
            self.assertIn("Result: OK", evidence)

    def test_status_reads_legacy_mingjie_state_when_new_state_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            legacy = project / ".mingjie"
            legacy.mkdir()
            (legacy / "STATE.md").write_text("current_stage: review\n", encoding="utf-8")

            result = self.run_harness("status", cwd=project)

            self.assertIn("legacy", result.stdout)
            self.assertIn(".mingjie/STATE.md", result.stdout)
            self.assertIn("current_stage: review", result.stdout)


if __name__ == "__main__":
    unittest.main()
