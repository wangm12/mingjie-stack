import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillContractTests(unittest.TestCase):
    def test_required_stage_skills_exist(self):
        required = {
            "mingjie-stack",
            "mingjie-intake",
            "mingjie-frame",
            "mingjie-plan",
            "mingjie-guard",
            "mingjie-build",
            "mingjie-review",
            "mingjie-verify",
            "mingjie-accept",
            "mingjie-ship",
            "mingjie-harness",
            "mingjie-bridge",
        }

        present = {
            path.parent.name
            for path in SKILLS.glob("*/SKILL.md")
        }

        self.assertTrue(required <= present)

    def test_each_skill_has_openai_metadata(self):
        missing = []
        for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
            metadata = skill_md.parent / "agents" / "openai.yaml"
            if not metadata.exists():
                missing.append(str(metadata.relative_to(ROOT)))

        self.assertEqual(missing, [])

    def test_stack_documents_uber_hard_stop(self):
        text = (SKILLS / "mingjie-stack" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Uber Repo Hard Stop", text)
        self.assertIn("uber-dev:", text)
        self.assertIn("uber-reviewer:", text)
        self.assertIn("prohibited", text.lower())

    def test_stack_requires_stage_transition_prompts(self):
        text = (SKILLS / "mingjie-stack" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Stage Transition Prompts", text)
        self.assertIn("Next suggested skill", text)
        self.assertIn("Proceed?", text)
        self.assertIn("Discuss extra items", text)
        self.assertIn("Update plan/implementation", text)
        self.assertIn("exit the active plan/automation", text)
        self.assertIn("normal discussion mode", text)

    def test_harness_scopes_learning(self):
        text = (SKILLS / "mingjie-harness" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Project scope", text)
        self.assertIn("User scope", text)
        self.assertIn("Org scope", text)
        self.assertIn("approval", text.lower())

    def test_route_fixtures_are_valid(self):
        fixture = ROOT / "tests" / "fixtures" / "skill_routes.json"
        cases = json.loads(fixture.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(cases), 5)
        for case in cases:
            self.assertIn("name", case)
            self.assertIn("prompt", case)
            self.assertIn("expected_route", case)


if __name__ == "__main__":
    unittest.main()
