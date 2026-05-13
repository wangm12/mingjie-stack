import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SERVER = Path(__file__).resolve().parents[1] / "mcp" / "agent_bridge_server.py"


class AgentBridgeMcpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cwd = self.home / "projects" / "demo"
        self.cwd.mkdir(parents=True)
        self.env = {
            **os.environ,
            "HOME": str(self.home),
            "MINGJIE_BRIDGE_SESSION": "mcp",
        }
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.addCleanup(self.stop_server)

    def stop_server(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if stream is not None and not stream.closed:
                stream.close()

    def rpc(self, method, params=None, request_id=1):
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.proc.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": method,
                    "params": params or {},
                }
            )
            + "\n"
        )
        self.proc.stdin.flush()
        return json.loads(self.proc.stdout.readline())

    def test_mcp_lists_and_calls_bridge_tools(self):
        initialized = self.rpc("initialize", request_id=1)
        self.assertEqual(initialized["result"]["serverInfo"]["name"], "mingjie-agent-bridge")

        listed = self.rpc("tools/list", request_id=2)
        tool_names = {tool["name"] for tool in listed["result"]["tools"]}
        self.assertIn("bridge_send", tool_names)
        self.assertIn("bridge_inbox", tool_names)

        sent = self.rpc(
            "tools/call",
            {
                "name": "bridge_send",
                "arguments": {
                    "sender": "codex",
                    "recipient": "claude",
                    "subject": "Review",
                    "body": "Please review.",
                    "files": ["plan.md"],
                },
            },
            request_id=3,
        )
        sent_payload = json.loads(sent["result"]["content"][0]["text"])

        inbox = self.rpc(
            "tools/call",
            {"name": "bridge_inbox", "arguments": {"agent": "claude"}},
            request_id=4,
        )
        inbox_payload = json.loads(inbox["result"]["content"][0]["text"])
        self.assertEqual([message["id"] for message in inbox_payload], [sent_payload["id"]])


class AgentBridgeAutoRegistrationTests(AgentBridgeMcpTests):
    """Inherits server fixture; verifies clientInfo-driven self-registration."""

    def setUp(self):
        super().setUp()
        # Restart server with TMUX_PANE in env so self-registration can fire.
        self._restart_server({"TMUX_PANE": "%42"})

    def _restart_server(self, extra_env: dict) -> None:
        self.stop_server()
        self.env.update(extra_env)
        self.proc = subprocess.Popen(
            [sys.executable, str(SERVER)],
            cwd=self.cwd,
            env=self.env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _initialize_as(self, client_name: str) -> None:
        self.rpc(
            "initialize",
            {"clientInfo": {"name": client_name, "version": "0.0.0"}},
            request_id=1,
        )

    def _read_status(self) -> dict:
        resp = self.rpc(
            "tools/call",
            {"name": "bridge_status", "arguments": {}},
            request_id=99,
        )
        return json.loads(resp["result"]["content"][0]["text"])

    def test_claude_code_auto_registers_as_claude(self):
        self._initialize_as("claude-code")
        status = self._read_status()
        self.assertIn("claude", status["agents"])
        self.assertEqual(status["agents"]["claude"]["pane"], "%42")

    def test_codex_mcp_client_auto_registers_as_codex(self):
        self._initialize_as("codex-mcp-client")
        status = self._read_status()
        self.assertIn("codex", status["agents"])
        self.assertEqual(status["agents"]["codex"]["pane"], "%42")

    def test_unknown_client_does_not_register(self):
        self._initialize_as("some-other-tool")
        status = self._read_status()
        self.assertEqual(status["agents"], {})

    def test_explicit_env_var_overrides_client_info(self):
        # Restart with MINGJIE_BRIDGE_AGENT set explicitly.
        self._restart_server({"MINGJIE_BRIDGE_AGENT": "custom-name"})
        self._initialize_as("claude-code")  # would normally map to "claude"
        status = self._read_status()
        self.assertIn("custom-name", status["agents"])
        self.assertNotIn("claude", status["agents"])


if __name__ == "__main__":
    unittest.main()
