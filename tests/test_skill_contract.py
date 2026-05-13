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

    def test_stack_documents_multi_agent_planning_workflow(self):
        stack_text = (SKILLS / "mingjie-stack" / "SKILL.md").read_text(encoding="utf-8")
        reference = SKILLS / "mingjie-stack" / "references" / "multi-agent-planning.md"

        self.assertTrue(reference.exists())
        ref_text = reference.read_text(encoding="utf-8")
        combined = f"{stack_text}\n{ref_text}"

        self.assertIn("Multi-Agent Planning", stack_text)
        self.assertIn("Intake -> Frame -> Multi-Agent Plan Drafts -> Synthesis -> Judge Final Plan -> Guard -> Build", combined)

        for role in [
            "Conservative Planner",
            "Aggressive Planner",
            "Pragmatic Planner",
            "Skeptic-Guard",
        ]:
            self.assertIn(role, combined)

        for artifact in [
            "BRIEF.md",
            "draft-conservative.md",
            "draft-aggressive.md",
            "draft-pragmatic.md",
            "draft-skeptic-guard.md",
            "synthesis.md",
            "final-plan.md",
        ]:
            self.assertIn(artifact, combined)

        for field in [
            "Goal:",
            "Context:",
            "Role:",
            "Constraints:",
            "Files:",
            "Requested action:",
            "Expected output:",
        ]:
            self.assertIn(field, combined)

        self.assertIn("advisory/read-only", combined)
        self.assertIn("native subagents", combined)
        self.assertIn("one final", combined)
        self.assertIn("Uber", combined)
        self.assertIn("generic GitHub", combined)

    def test_harness_scopes_learning(self):
        text = (SKILLS / "mingjie-harness" / "SKILL.md").read_text(encoding="utf-8")
        stack_text = (SKILLS / "mingjie-stack" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Project scope", text)
        self.assertIn("User scope", text)
        self.assertIn("Org scope", text)
        self.assertIn("approval", text.lower())
        self.assertIn("docs/mingjie-stack/", text)
        self.assertIn("docs/mingjie-stack/STATE.md", stack_text)
        self.assertIn("legacy `.mingjie/STATE.md`", text)
        self.assertIn("mingjie-harness init", text)
        self.assertIn("Run Retention", text)
        self.assertIn("runs prune", text)
        self.assertIn("PINNED", text)
        self.assertIn("Multi-Agent Planning Artifacts", text)
        self.assertIn("multi-agent init", text)

    def test_stack_documents_hook_policy(self):
        text = (SKILLS / "mingjie-stack" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Hook Policy", text)
        self.assertIn("./setup --hooks", text)
        self.assertIn("scripts/mingjie-hook", text)
        self.assertIn("PreToolUse", text)
        self.assertIn("PostToolUse", text)
        self.assertIn("Stop", text)
        self.assertIn("not a complete security boundary", text)

    def test_route_fixtures_are_valid(self):
        fixture = ROOT / "tests" / "fixtures" / "skill_routes.json"
        cases = json.loads(fixture.read_text(encoding="utf-8"))

        self.assertGreaterEqual(len(cases), 5)
        for case in cases:
            self.assertIn("name", case)
            self.assertIn("prompt", case)
            self.assertIn("expected_route", case)

    def test_route_fixtures_cover_multi_agent_planning(self):
        fixture = ROOT / "tests" / "fixtures" / "skill_routes.json"
        cases = json.loads(fixture.read_text(encoding="utf-8"))
        cases_by_name = {case["name"]: case for case in cases}

        for name in [
            "multi_agent_chinese_plan",
            "multi_agent_personality_debate",
            "large_risky_tmux_agents",
        ]:
            self.assertIn(name, cases_by_name)
            self.assertIn("Multi-Agent Plan Drafts", cases_by_name[name]["expected_route"])


if __name__ == "__main__":
    unittest.main()
