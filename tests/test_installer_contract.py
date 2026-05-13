import importlib.util
import io
import json
from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
import unittest
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "install"


def load_install_module():
    loader = SourceFileLoader("mingjie_install", str(INSTALL))
    spec = importlib.util.spec_from_loader("mingjie_install", loader)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InstallerContractTests(unittest.TestCase):
    def test_assume_yes_accepts_prompt_default(self):
        install = load_install_module()

        with redirect_stdout(io.StringIO()):
            self.assertTrue(install.ask("Install?", default=True, assume_yes=True))
            self.assertFalse(install.ask("Overwrite?", default=False, assume_yes=True))

    def test_merge_json_hooks_preserves_existing_hooks(self):
        install = load_install_module()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": "existing analytics hook",
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            install.merge_json_hooks(
                path,
                {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": "mingjie-hook"}]}]}},
                dry_run=False,
            )

            merged = json.loads(path.read_text(encoding="utf-8"))
            commands = [
                hook["command"]
                for item in merged["hooks"]["PreToolUse"]
                for hook in item["hooks"]
            ]
            self.assertIn("existing analytics hook", commands)
            self.assertIn("mingjie-hook", commands)

    def test_enable_codex_hooks_adds_feature_without_dropping_config(self):
        install = load_install_module()

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text('model = "gpt-5.5"\n', encoding="utf-8")

            install.ensure_codex_hooks_feature(path, dry_run=False)

            text = path.read_text(encoding="utf-8")
            self.assertIn('model = "gpt-5.5"', text)
            self.assertIn("[features]", text)
            self.assertIn("codex_hooks = true", text)


if __name__ == "__main__":
    unittest.main()
