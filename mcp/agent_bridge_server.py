#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.agent_bridge_core import AgentBridge


_client_info: dict[str, Any] = {}

# Maps a substring of MCP clientInfo.name to the bridge identity to register.
# Discovered values: Claude Code sends "claude-code"; Codex sends "codex-mcp-client".
_NAME_PATTERNS = (
    ("claude", "claude"),
    ("codex", "codex"),
    ("cursor", "cursor"),
)


def _bridge_identity() -> str | None:
    """Return the agent name we should register as, or None if unknown.

    Priority: explicit MINGJIE_BRIDGE_AGENT env var > clientInfo.name substring match.
    """
    explicit = os.environ.get("MINGJIE_BRIDGE_AGENT")
    if explicit:
        return explicit
    name = (_client_info.get("name") or "").lower()
    for pattern, identity in _NAME_PATTERNS:
        if pattern in name:
            return identity
    return None


def _ensure_self_registered() -> None:
    """If we know our identity and pane, ensure the bridge has us registered.

    No-ops when:
      - clientInfo not yet captured (initialize hasn't run) AND no MINGJIE_BRIDGE_AGENT
      - TMUX_PANE not in env
      - already registered for this pane
    Silently swallows registration errors.
    """
    name = _bridge_identity()
    pane = os.environ.get("TMUX_PANE")
    if not (name and pane):
        return
    try:
        bridge = AgentBridge.from_env()
        existing = bridge.status()["agents"].get(name)
        if existing and existing.get("pane") == pane:
            return
        bridge.register(agent=name, pane=pane)
    except Exception:
        pass


TOOLS: list[dict[str, Any]] = [
    {
        "name": "bridge_send",
        "description": "Send a message to another agent in the current tmux-session bridge.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sender": {"type": "string"},
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "files": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["sender", "recipient", "subject", "body"],
        },
    },
    {
        "name": "bridge_inbox",
        "description": "List messages addressed to an agent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "unread_only": {"type": "boolean", "default": True},
            },
            "required": ["agent"],
        },
    },
    {
        "name": "bridge_read",
        "description": "Read a bridge message by id.",
        "inputSchema": {
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
        },
    },
    {
        "name": "bridge_reply",
        "description": "Reply to a bridge message.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string"},
                "sender": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["message_id", "sender", "body"],
        },
    },
    {
        "name": "bridge_mark_done",
        "description": "Mark a bridge message as done.",
        "inputSchema": {
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
        },
    },
    {
        "name": "bridge_threads",
        "description": "List bridge thread summaries for the current tmux session.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "bridge_register_agent",
        "description": "Register an agent name with a tmux pane id.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "pane": {"type": "string"},
            },
            "required": ["agent", "pane"],
        },
    },
    {
        "name": "bridge_status",
        "description": "Show bridge session state, registered agents, and counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "bridge_notify",
        "description": "Send a tmux notification prompt to a registered agent pane.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["agent"],
        },
    },
]


def _result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _tool_result(value: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(value, indent=2, sort_keys=True),
            }
        ],
        "isError": False,
    }


def _call_tool(name: str, arguments: dict[str, Any]) -> Any:
    bridge = AgentBridge.from_env()

    if name == "bridge_send":
        return bridge.send(
            sender=arguments["sender"],
            recipient=arguments["recipient"],
            subject=arguments["subject"],
            body=arguments["body"],
            files=arguments.get("files") or [],
        )
    if name == "bridge_inbox":
        return bridge.inbox(
            agent=arguments["agent"],
            unread_only=arguments.get("unread_only", True),
        )
    if name == "bridge_read":
        return bridge.read(arguments["message_id"])
    if name == "bridge_reply":
        return bridge.reply(
            message_id=arguments["message_id"],
            sender=arguments["sender"],
            body=arguments["body"],
        )
    if name == "bridge_mark_done":
        return bridge.mark_done(arguments["message_id"])
    if name == "bridge_threads":
        return bridge.threads()
    if name == "bridge_register_agent":
        return bridge.register(agent=arguments["agent"], pane=arguments["pane"])
    if name == "bridge_status":
        return bridge.status()
    if name == "bridge_notify":
        return bridge.notify(agent=arguments["agent"], text=arguments.get("text"))

    raise KeyError(f"unknown tool: {name}")


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if request_id is None:
        return None

    try:
        if method == "initialize":
            _client_info.update(params.get("clientInfo") or {})
            return _result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "mingjie-agent-bridge",
                        "version": "0.1.0",
                    },
                },
            )
        if method == "tools/list":
            return _result(request_id, {"tools": TOOLS})
        if method == "tools/call":
            _ensure_self_registered()
            value = _call_tool(params["name"], params.get("arguments") or {})
            return _result(request_id, _tool_result(value))

        return _error(request_id, -32601, f"method not found: {method}")
    except Exception as exc:
        return _error(request_id, -32000, str(exc))


def main() -> int:
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = handle(request)
        except json.JSONDecodeError as exc:
            response = _error(None, -32700, str(exc))

        if response is not None:
            sys.stdout.write(json.dumps(response, separators=(",", ":")))
            sys.stdout.write("\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
