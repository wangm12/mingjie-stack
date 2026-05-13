import json
import os
import tempfile
import unittest
from pathlib import Path

from mcp.agent_bridge_core import AgentBridge


class AgentBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.cwd = self.home / "projects" / "demo"
        self.cwd.mkdir(parents=True)
        self.env = {
            "HOME": str(self.home),
            "MINGJIE_BRIDGE_SESSION": "main:work",
        }

    def test_send_and_inbox_are_scoped_by_tmux_session(self):
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)

        message = bridge.send(
            sender="codex",
            recipient="claude",
            subject="Review plan",
            body="Please review the plan.",
            files=["src/app.py"],
        )

        self.assertEqual(message["session"], "main:work")
        self.assertEqual(message["to"], "claude")
        self.assertEqual(message["project_root"], str(self.cwd.resolve()))
        self.assertEqual(message["files"], ["src/app.py"])

        inbox = bridge.inbox(agent="claude")
        self.assertEqual([item["id"] for item in inbox], [message["id"]])

        other = AgentBridge.from_env(
            cwd=self.cwd,
            environ={**self.env, "MINGJIE_BRIDGE_SESSION": "other"},
        )
        self.assertEqual(other.inbox(agent="claude"), [])

    def test_reply_stays_in_thread_and_mark_done_hides_from_open_inbox(self):
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        original = bridge.send("codex", "claude", "Review", "Thoughts?")

        reply = bridge.reply(
            message_id=original["id"],
            sender="claude",
            body="Looks sound.",
        )

        self.assertEqual(reply["thread_id"], original["thread_id"])
        self.assertEqual(reply["parent_id"], original["id"])
        self.assertEqual(reply["to"], "codex")

        self.assertEqual(len(bridge.inbox("codex")), 1)
        bridge.mark_done(reply["id"])
        self.assertEqual(bridge.inbox("codex"), [])
        self.assertEqual(len(bridge.inbox("codex", unread_only=False)), 1)

    def test_register_pane_and_status(self):
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)

        registration = bridge.register(agent="codex", pane="%1")
        status = bridge.status()

        self.assertEqual(registration["agent"], "codex")
        self.assertEqual(status["session"], "main:work")
        self.assertEqual(status["agents"]["codex"]["pane"], "%1")
        self.assertEqual(status["message_count"], 0)

    def test_threads_group_related_messages(self):
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        original = bridge.send("codex", "claude", "Review", "Thoughts?")
        reply = bridge.reply(original["id"], "claude", "Looks sound.")

        threads = bridge.threads()

        self.assertEqual(len(threads), 1)
        self.assertEqual(threads[0]["thread_id"], original["thread_id"])
        self.assertEqual(threads[0]["message_ids"], [original["id"], reply["id"]])

    def test_events_are_json_lines(self):
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        bridge.send("codex", "claude", "Subject", "Body")

        lines = bridge.events_path.read_text().splitlines()
        self.assertEqual(len(lines), 1)
        event = json.loads(lines[0])
        self.assertEqual(event["type"], "message")

    def test_send_auto_notifies_registered_recipient(self):
        from unittest import mock
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        bridge.register(agent="claude", pane="%99")

        with mock.patch("mcp.agent_bridge_core.subprocess.run") as run:
            bridge.send("codex", "claude", "ping", "hello")

        # Two tmux send-keys calls per notify (text + Enter)
        self.assertEqual(run.call_count, 2)
        first_call_args = run.call_args_list[0][0][0]
        self.assertEqual(first_call_args[:4], ["tmux", "send-keys", "-t", "%99"])

    def test_send_does_not_error_when_recipient_unregistered(self):
        from unittest import mock
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)

        with mock.patch("mcp.agent_bridge_core.subprocess.run") as run:
            bridge.send("codex", "claude", "ping", "hello")

        run.assert_not_called()

    def test_send_swallows_tmux_failure(self):
        from unittest import mock
        import subprocess as sp
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        bridge.register(agent="claude", pane="%bogus")

        with mock.patch(
            "mcp.agent_bridge_core.subprocess.run",
            side_effect=sp.CalledProcessError(1, "tmux"),
        ):
            # must not raise
            msg = bridge.send("codex", "claude", "ping", "hello")
        self.assertEqual(msg["to"], "claude")

    def test_reply_auto_notifies_original_sender(self):
        from unittest import mock
        bridge = AgentBridge.from_env(cwd=self.cwd, environ=self.env)
        bridge.register(agent="codex", pane="%55")
        original = bridge.send("codex", "claude", "ping", "hello", notify_recipient=False)

        with mock.patch("mcp.agent_bridge_core.subprocess.run") as run:
            bridge.reply(original["id"], "claude", "pong")

        self.assertEqual(run.call_count, 2)
        target_pane = run.call_args_list[0][0][0][3]
        self.assertEqual(target_pane, "%55")


if __name__ == "__main__":
    unittest.main()
