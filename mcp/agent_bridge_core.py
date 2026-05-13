from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_MARKERS = (".git", "AGENTS.md", "CLAUDE.md", "package.json", "pyproject.toml")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_path_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return safe.strip("._") or "default"


def _event_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def infer_project_root(cwd: Path) -> Path:
    cwd = cwd.resolve()
    for current in (cwd, *cwd.parents):
        if any((current / marker).exists() for marker in PROJECT_MARKERS):
            return current
    return cwd


def detect_tmux_session(environ: dict[str, str] | None = None) -> str:
    environ = environ or os.environ
    explicit = environ.get("MINGJIE_BRIDGE_SESSION")
    if explicit:
        return explicit

    pane = environ.get("TMUX_PANE")
    if pane:
        try:
            result = subprocess.run(
                ["tmux", "display-message", "-p", "-t", pane, "#S"],
                check=True,
                capture_output=True,
                text=True,
            )
            session = result.stdout.strip()
            if session:
                return session
        except (OSError, subprocess.CalledProcessError):
            return "default"

    return "default"


class AgentBridge:
    def __init__(self, *, home: Path, session: str, cwd: Path):
        self.home = home
        self.session = session
        self.cwd = cwd.resolve()
        self.project_root = infer_project_root(self.cwd)
        self.session_dir = (
            self.home
            / ".mingjie-stack"
            / "agent-bridge"
            / "sessions"
            / _safe_path_name(session)
        )
        self.events_path = self.session_dir / "messages.jsonl"
        self.artifacts_dir = self.session_dir / "artifacts"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(
        cls,
        *,
        cwd: str | Path | None = None,
        environ: dict[str, str] | None = None,
    ) -> "AgentBridge":
        environ = environ or os.environ
        home = Path(environ.get("MINGJIE_BRIDGE_HOME") or environ.get("HOME", "~")).expanduser()
        working_dir = Path(cwd or environ.get("PWD") or os.getcwd())
        return cls(home=home, session=detect_tmux_session(environ), cwd=working_dir)

    def send(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        files: list[str] | None = None,
        *,
        thread_id: str | None = None,
        parent_id: str | None = None,
        notify_recipient: bool = True,
    ) -> dict[str, Any]:
        message = {
            "type": "message",
            "id": _event_id("msg"),
            "thread_id": thread_id or _event_id("thread"),
            "parent_id": parent_id,
            "session": self.session,
            "from": sender,
            "to": recipient,
            "project_root": str(self.project_root),
            "cwd": str(self.cwd),
            "subject": subject,
            "body": body,
            "files": files or [],
            "status": "open",
            "created_at": _now(),
        }
        self._append_event(message)
        if notify_recipient:
            self._maybe_notify(recipient, sender, subject)
        return message

    def _maybe_notify(self, recipient: str, sender: str, subject: str) -> None:
        """Notify recipient if registered. Silent on any failure."""
        try:
            self.notify(
                recipient,
                text=f"You have a new bridge message from {sender} ({subject}). Please check your inbox and reply.",
            )
        except (KeyError, subprocess.CalledProcessError, OSError):
            pass

    def reply(self, message_id: str, sender: str, body: str) -> dict[str, Any]:
        original = self.read(message_id)
        return self.send(
            sender=sender,
            recipient=original["from"],
            subject=f"Re: {original['subject']}",
            body=body,
            thread_id=original["thread_id"],
            parent_id=original["id"],
        )

    def inbox(self, agent: str, unread_only: bool = True) -> list[dict[str, Any]]:
        messages = [
            message
            for message in self._projected_messages()
            if message["to"] == agent and (not unread_only or message["status"] == "open")
        ]
        return sorted(messages, key=lambda item: item["created_at"])

    def read(self, message_id: str) -> dict[str, Any]:
        for message in self._projected_messages():
            if message["id"] == message_id:
                return message
        raise KeyError(f"message not found: {message_id}")

    def mark_done(self, message_id: str) -> dict[str, Any]:
        self.read(message_id)
        event = {
            "type": "status",
            "id": _event_id("evt"),
            "message_id": message_id,
            "status": "done",
            "created_at": _now(),
        }
        self._append_event(event)
        return event

    def threads(self) -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for message in sorted(self._projected_messages(), key=lambda item: item["created_at"]):
            grouped.setdefault(message["thread_id"], []).append(message)

        summaries = []
        for thread_id, messages in grouped.items():
            summaries.append(
                {
                    "thread_id": thread_id,
                    "subject": messages[0]["subject"],
                    "message_ids": [message["id"] for message in messages],
                    "participants": sorted(
                        {message["from"] for message in messages}
                        | {message["to"] for message in messages}
                    ),
                    "open_count": sum(1 for message in messages if message["status"] == "open"),
                    "updated_at": messages[-1]["created_at"],
                }
            )
        return sorted(summaries, key=lambda item: item["updated_at"])

    def register(self, agent: str, pane: str) -> dict[str, Any]:
        event = {
            "type": "register",
            "id": _event_id("reg"),
            "session": self.session,
            "agent": agent,
            "pane": pane,
            "project_root": str(self.project_root),
            "cwd": str(self.cwd),
            "created_at": _now(),
        }
        self._append_event(event)
        return event

    def status(self) -> dict[str, Any]:
        events = self._read_events()
        agents: dict[str, dict[str, Any]] = {}
        for event in events:
            if event.get("type") == "register":
                agents[event["agent"]] = {
                    "pane": event["pane"],
                    "project_root": event.get("project_root"),
                    "cwd": event.get("cwd"),
                    "registered_at": event["created_at"],
                }

        messages = [event for event in events if event.get("type") == "message"]
        open_count = sum(1 for message in self._projected_messages() if message["status"] == "open")
        return {
            "session": self.session,
            "session_dir": str(self.session_dir),
            "agents": agents,
            "message_count": len(messages),
            "open_count": open_count,
        }

    def notify(self, agent: str, text: str | None = None) -> dict[str, Any]:
        status = self.status()
        registration = status["agents"].get(agent)
        if not registration:
            raise KeyError(f"agent is not registered: {agent}")

        pane = registration["pane"]
        message = text or "mingjie-bridge: check your inbox"
        subprocess.run(["tmux", "send-keys", "-t", pane, "-l", message], check=True)
        subprocess.run(["tmux", "send-keys", "-t", pane, "Enter"], check=True)
        return {"agent": agent, "pane": pane, "notified": True, "text": message}

    def _append_event(self, event: dict[str, Any]) -> None:
        line = json.dumps(event, sort_keys=True) + "\n"
        with self.events_path.open("a", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            handle.write(line)

    def _read_events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        with self.events_path.open("r", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
            text = handle.read()
        events = []
        for line in text.splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def _projected_messages(self) -> list[dict[str, Any]]:
        messages: dict[str, dict[str, Any]] = {}
        statuses: dict[str, str] = {}
        for event in self._read_events():
            event_type = event.get("type")
            if event_type == "message":
                messages[event["id"]] = dict(event)
            elif event_type == "status":
                statuses[event["message_id"]] = event["status"]

        for message_id, status in statuses.items():
            if message_id in messages:
                messages[message_id]["status"] = status
        return list(messages.values())
