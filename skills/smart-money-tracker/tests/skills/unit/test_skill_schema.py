from pathlib import Path

import pytest

from skills_testing.models import SkillContract, SkillMetadata, ValidationResult
from skills_testing.skill_loader import load_all_skills, load_skill, parse_frontmatter, validate_skill_contract

SKILLS_DIR = Path(__file__).parent.parent / "fixtures" / "skills"


class TestParseFrontmatter:
    def test_valid_frontmatter(self):
        content = "---\nname: test-skill\ndescription: A test skill\n---\n# Test Skill\n\nContent here."
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter["name"] == "test-skill"
        assert frontmatter["description"] == "A test skill"
        assert "# Test Skill" in body

    def test_missing_frontmatter_raises(self):
        with pytest.raises(ValueError, match="No YAML frontmatter"):
            parse_frontmatter("# No frontmatter\n\nJust content.")

    def test_empty_frontmatter(self):
        content = "---\n---\n# Test\n"
        frontmatter, body = parse_frontmatter(content)
        assert frontmatter == {}
        assert "# Test" in body


class TestLoadSkill:
    def test_load_existing_skill(self):
        skill_path = SKILLS_DIR / "test-driven-development" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("Skill not found")
        metadata, body = load_skill(skill_path)
        assert metadata.name == "test-driven-development"
        assert len(metadata.description) > 0
        assert "## Overview" in body

    def test_load_skill_with_contracts(self):
        skill_path = SKILLS_DIR / "test-driven-development" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("Skill not found")
        metadata, body = load_skill(skill_path)
        assert isinstance(metadata.contracts, SkillContract)


class TestLoadAllSkills:
    def test_loads_all_skills(self):
        skills = load_all_skills(SKILLS_DIR)
        assert len(skills) > 0
        assert "test-skill" in skills

    def test_all_skills_have_valid_frontmatter(self):
        skills = load_all_skills(SKILLS_DIR)
        errors = []
        for name, (metadata, body) in skills.items():
            if metadata is None:
                errors.append(f"{name}: {body}")
        assert not errors, f"Skills with invalid frontmatter: {errors}"


class TestValidateSkillContract:
    def test_skill_with_no_contract_passes(self):
        metadata = SkillMetadata(name="test", description="test")
        body = "# Test\n\n## Overview\n"
        result = validate_skill_contract("test", metadata, body)
        assert result.passed

    def test_missing_required_section(self):
        metadata = SkillMetadata(
            name="test",
            description="test",
            contracts=SkillContract(required_sections=["verification"]),
        )
        body = "# Test\n\n## Overview\n"
        result = validate_skill_contract("test", metadata, body)
        assert not result.passed
        assert "verification" in result.missing_sections

    def test_forbidden_pattern_found(self):
        metadata = SkillMetadata(
            name="test",
            description="test",
            contracts=SkillContract(forbidden_patterns=["as any"]),
        )
        body = "# Test\n\nUse `as any` to suppress."
        result = validate_skill_contract("test", metadata, body)
        assert not result.passed
        assert "as any" in result.forbidden_found


class TestSkillMetadataModel:
    def test_valid_metadata(self):
        data = {
            "name": "test-skill",
            "description": "A test skill",
            "contracts": {
                "required_sections": ["overview"],
                "verification_required": True,
            },
        }
        metadata = SkillMetadata(**data)
        assert metadata.name == "test-skill"
        assert metadata.contracts.verification_required

    def test_default_contract(self):
        metadata = SkillMetadata(name="test", description="test")
        assert metadata.contracts.required_sections == []
        assert not metadata.contracts.verification_required
