import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "mingjie-hook"
HARNESS = ROOT / "scripts" / "mingjie-harness"


class HookAdapterTests(unittest.TestCase):
    def run_hook(self, payload: dict, *, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(HOOK), "--platform", "auto"],
            input=json.dumps(payload),
            cwd=cwd,
            capture_output=True,
            text=True,
        )

    def test_session_start_outputs_harness_state_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state_dir = project / "docs" / "mingjie-stack"
            state_dir.mkdir(parents=True)
            (state_dir / "STATE.md").write_text("- current_stage: review\n", encoding="utf-8")

            result = self.run_hook({"hook_event_name": "SessionStart"}, cwd=project)

            self.assertEqual(result.returncode, 0)
            self.assertIn("Mingjie Harness state", result.stdout)
            self.assertIn("current_stage: review", result.stdout)

    def test_pre_tool_use_blocks_destructive_git_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            payload = {
                "hook_event_name": "PreToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "git reset --hard HEAD~1"},
            }

            result = self.run_hook(payload, cwd=project)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Blocked", result.stderr)
            self.assertIn("git reset --hard", result.stderr)

    def test_post_tool_use_appends_evidence_to_active_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            subprocess.run(
                [sys.executable, str(HARNESS), "start-run", "--id", "run-1"],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "python3 -m unittest discover tests"},
                "tool_response": {"success": True},
            }

            result = self.run_hook(payload, cwd=project)

            evidence = (
                project
                / "docs"
                / "mingjie-stack"
                / "runs"
                / "run-1"
                / "EVIDENCE.md"
            ).read_text(encoding="utf-8")
            self.assertEqual(result.returncode, 0)
            self.assertIn("python3 -m unittest discover tests", evidence)
            self.assertIn("Result: OK", evidence)

    def test_post_tool_use_defaults_successful_event_to_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            subprocess.run(
                [sys.executable, str(HARNESS), "start-run", "--id", "run-1"],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = {
                "hook_event_name": "PostToolUse",
                "tool_name": "Bash",
                "tool_input": {"command": "echo ok"},
            }

            result = self.run_hook(payload, cwd=project)

            evidence = (
                project
                / "docs"
                / "mingjie-stack"
                / "runs"
                / "run-1"
                / "EVIDENCE.md"
            ).read_text(encoding="utf-8")
            self.assertEqual(result.returncode, 0)
            self.assertIn("Result: OK", evidence)

    def test_stop_blocks_completion_claim_without_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            subprocess.run(
                [sys.executable, str(HARNESS), "start-run", "--id", "run-1"],
                cwd=project,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = {
                "hook_event_name": "Stop",
                "assistant_response": "Done. The implementation is complete.",
            }

            result = self.run_hook(payload, cwd=project)

            self.assertEqual(result.returncode, 2)
            self.assertIn("No fresh Harness verification evidence", result.stderr)


if __name__ == "__main__":
    unittest.main()
