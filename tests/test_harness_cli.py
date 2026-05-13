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

    def test_runs_list_reports_pinned_and_unpinned_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.run_harness("start-run", "--id", "20260501-older", cwd=project)
            self.run_harness("start-run", "--id", "20260502-newer", cwd=project)
            self.run_harness("runs", "pin", "20260501-older", cwd=project)

            result = self.run_harness("runs", "list", cwd=project)

            self.assertIn("20260501-older", result.stdout)
            self.assertIn("PINNED", result.stdout)
            self.assertIn("20260502-newer", result.stdout)

    def test_runs_summarize_writes_index_and_monthly_archive(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.run_harness("start-run", "--id", "20260501-old", cwd=project)
            self.run_harness(
                "append-evidence",
                "--run-id",
                "20260501-old",
                "--title",
                "tests",
                "--command",
                "python3 -m unittest discover tests",
                "--result",
                "OK",
                cwd=project,
            )

            result = self.run_harness("runs", "summarize", "--run-id", "20260501-old", cwd=project)

            index = (project / "docs" / "mingjie-stack" / "RUNS_INDEX.md").read_text(encoding="utf-8")
            archive = (
                project
                / "docs"
                / "mingjie-stack"
                / "runs"
                / "archive"
                / "2026-05.md"
            ).read_text(encoding="utf-8")
            self.assertIn("20260501-old", result.stdout)
            self.assertIn("20260501-old", index)
            self.assertIn("Result: OK", archive)
            self.assertIn("python3 -m unittest discover tests", archive)

    def test_runs_prune_dry_run_keeps_recent_and_pinned_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for run_id in ["20260501-old", "20260502-pinned", "20260503-new"]:
                self.run_harness("start-run", "--id", run_id, cwd=project)
            self.run_harness("runs", "pin", "20260502-pinned", cwd=project)

            result = self.run_harness("runs", "prune", "--keep", "1", "--dry-run", cwd=project)

            self.assertIn("Would prune 20260501-old", result.stdout)
            self.assertNotIn("Would prune 20260502-pinned", result.stdout)
            self.assertTrue((project / "docs" / "mingjie-stack" / "runs" / "20260501-old").exists())

    def test_runs_prune_deletes_unpinned_old_runs_after_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for run_id in ["20260501-old", "20260502-new"]:
                self.run_harness("start-run", "--id", run_id, cwd=project)

            self.run_harness("runs", "prune", "--keep", "1", "--yes", cwd=project)

            self.assertFalse((project / "docs" / "mingjie-stack" / "runs" / "20260501-old").exists())
            self.assertTrue((project / "docs" / "mingjie-stack" / "runs" / "20260502-new").exists())
            index = (project / "docs" / "mingjie-stack" / "RUNS_INDEX.md").read_text(encoding="utf-8")
            self.assertIn("20260501-old", index)

    def test_multi_agent_init_creates_brief_roles_and_skeletons(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)

            result = self.run_harness(
                "multi-agent",
                "init",
                "--run-id",
                "run-1",
                "--goal",
                "Add hooks",
                "--context",
                "Existing project uses Mingjie Stack",
                cwd=project,
            )

            base = project / "docs" / "mingjie-stack" / "runs" / "run-1" / "multi-agent"
            self.assertIn("multi-agent", result.stdout)
            self.assertTrue((base / "BRIEF.md").exists())
            for name in [
                "draft-conservative.md",
                "draft-aggressive.md",
                "draft-pragmatic.md",
                "draft-skeptic-guard.md",
                "synthesis.md",
                "final-plan.md",
            ]:
                self.assertTrue((base / name).exists())
            self.assertIn("Add hooks", (base / "BRIEF.md").read_text(encoding="utf-8"))
            self.assertIn("Conservative Planner", (base / "draft-conservative.md").read_text(encoding="utf-8"))

    def test_multi_agent_status_reports_missing_and_ready_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.run_harness("multi-agent", "init", "--run-id", "run-1", "--goal", "Plan X", cwd=project)

            result = self.run_harness("multi-agent", "status", "--run-id", "run-1", cwd=project)

            self.assertIn("draft-conservative.md: missing", result.stdout)
            self.assertIn("final-plan.md: skeleton", result.stdout)

            draft = (
                project
                / "docs"
                / "mingjie-stack"
                / "runs"
                / "run-1"
                / "multi-agent"
                / "draft-conservative.md"
            )
            draft.write_text("# Conservative Planner\n\nRecommended approach:\nShip it.\n", encoding="utf-8")

            result = self.run_harness("multi-agent", "status", "--run-id", "run-1", cwd=project)

            self.assertIn("draft-conservative.md: ready", result.stdout)

    def test_multi_agent_send_bridge_dry_run_prints_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.run_harness("multi-agent", "init", "--run-id", "run-1", "--goal", "Plan X", cwd=project)

            result = self.run_harness("multi-agent", "send-bridge", "--run-id", "run-1", "--dry-run", cwd=project)

            self.assertIn("mingjie-bridge send", result.stdout)
            self.assertIn("--to claude", result.stdout)
            self.assertIn("--to codex", result.stdout)


if __name__ == "__main__":
    unittest.main()
