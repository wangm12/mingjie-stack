import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / "scripts" / "mingjie-bridge"


class AgentBridgeCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cwd = self.home / "projects" / "demo"
        self.cwd.mkdir(parents=True)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "MINGJIE_BRIDGE_SESSION": "cli",
        }

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=self.cwd,
            env=self.env,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_send_inbox_reply_done_flow(self):
        sent = json.loads(
            self.run_cli(
                "send",
                "--from",
                "codex",
                "--to",
                "claude",
                "--subject",
                "Review plan",
                "--body",
                "Please review.",
                "--file",
                "plan.md",
            ).stdout
        )

        inbox = json.loads(self.run_cli("inbox", "--for", "claude").stdout)
        self.assertEqual([message["id"] for message in inbox], [sent["id"]])

        reply = json.loads(
            self.run_cli(
                "reply",
                sent["id"],
                "--from",
                "claude",
                "--body",
                "Looks good.",
            ).stdout
        )
        self.assertEqual(reply["to"], "codex")

        self.run_cli("done", reply["id"])
        self.assertEqual(json.loads(self.run_cli("inbox", "--for", "codex").stdout), [])

    def test_register_and_status(self):
        self.run_cli("register", "codex", "--pane", "%1")
        status = json.loads(self.run_cli("status").stdout)

        self.assertEqual(status["session"], "cli")
        self.assertEqual(status["agents"]["codex"]["pane"], "%1")

    def test_config_prints_tool_specific_mcp_snippet(self):
        codex = self.run_cli("config", "--tool", "codex").stdout
        claude = self.run_cli("config", "--tool", "claude").stdout

        self.assertIn("[mcp_servers.mingjie_agent_bridge]", codex)
        self.assertIn(str(Path(__file__).resolve().parents[1] / "mcp" / "agent_bridge_server.py"), codex)
        self.assertIn('"mingjie-agent-bridge"', claude)


if __name__ == "__main__":
    unittest.main()
