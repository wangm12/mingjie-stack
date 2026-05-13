import importlib.util
import io
from contextlib import redirect_stdout
from importlib.machinery import SourceFileLoader
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()
