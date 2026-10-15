import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_brd.py"
SPEC = importlib.util.spec_from_file_location("check_brd", MODULE_PATH)
check_brd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_brd)


SAMPLE = """# BRD

## 1. Problem statement
The steering group must decide whether a hypothetical pilot is worth further study.

## 2. Decision owner and stakeholders

### Decision owner

The steering group owns the pilot decision.

### Stakeholders

| Role | Need |
| --- | --- |
| Learner role | Understand hypothetical program options |
| Finance role | Compare scenario costs |

## 3. Objectives
- Compare hypothetical program demand with a venue capacity limit.
- Identify evidence needed for a transparent pilot decision.

## 4. Scope and non-goals
### In scope
- Compare a small set of hypothetical program scenarios.
### Out of scope
- Claiming actual demand or identifying residents.

## 5. Assumptions and evidence plan
| Assumption | Status | Verification |
| --- | --- | --- |
| Scenario attendance | Hypothetical | Gather consent-based pilot signups |
| Scenario rental cost | Hypothetical | Verify quotes with venue providers |

## 6. Functional requirements
| ID | Requirement | Evidence |
| --- | --- | --- |
| FR-1 | Compare program options | Reviewer sees a comparison table |

## 7. Nonfunctional requirements
| ID | Requirement | Evidence |
| --- | --- | --- |
| NFR-1 | Use synthetic non-identifying data | No personal fields are present |

## 8. Success metrics and decision KPIs
| KPI | Definition and unit | Evidence | Proposed threshold |
| --- | --- | --- | --- |
| Budget fit | Cost in dollars | Scenario budget | Proposed for stakeholder review |
| Capacity fit | Attendees per event | Venue capacity | Hypothetical proposal |

## 9. Risks, ethics, and limitations
- **Bias and representation**: a self-selected sample may not represent preferences.
- **Uncertainty**: scenario values cannot establish real demand.
- **Responsible use**: analysis is decision support, not proof.

## 10. Open questions
- Verify accessible venues, costs, and consent-based interest before a real decision.
"""


class CheckBrdTests(unittest.TestCase):
    def sections(self, text=SAMPLE):
        return check_brd.read_sections(text)

    def test_complete_sample_passes_all_steps(self):
        sections = self.sections()
        self.assertEqual(check_brd.check_step_1(sections), [])
        self.assertEqual(check_brd.check_step_2(sections), [])
        self.assertEqual(check_brd.check_step_3(sections), [])
        self.assertEqual(check_brd.check_all(sections), [])

    def test_missing_stakeholder_roles_are_reported(self):
        text = SAMPLE.replace("| Learner role | Understand hypothetical program options |\n", "")
        errors = check_brd.check_step_1(self.sections(text))
        self.assertTrue(any("two stakeholder roles" in error for error in errors))

    def test_missing_decision_owner_is_reported(self):
        text = SAMPLE.replace("The steering group owns the pilot decision.", "TODO: Identify the decision owner.")
        errors = check_brd.check_step_1(self.sections(text))
        self.assertTrue(any("decision-owner role" in error for error in errors))

    def test_incomplete_stakeholder_row_is_not_counted(self):
        text = SAMPLE.replace(
            "| Learner role | Understand hypothetical program options |",
            "| Learner role | |",
        )
        errors = check_brd.check_step_1(self.sections(text))
        self.assertTrue(any("two stakeholder roles" in error for error in errors))

    def test_unlabeled_assumption_is_reported(self):
        text = SAMPLE.replace("| Scenario attendance | Hypothetical |", "| Scenario attendance | Estimate |")
        errors = check_brd.check_step_2(self.sections(text))
        self.assertTrue(any("label each assumption" in error for error in errors))

    def test_unmarked_kpi_threshold_is_reported(self):
        text = SAMPLE.replace("Proposed for stakeholder review", "80%")
        errors = check_brd.check_step_3(self.sections(text))
        self.assertTrue(any("label each threshold" in error for error in errors))

    def test_missing_ethics_prompts_are_reported(self):
        text = SAMPLE.replace("- **Bias and representation**:", "- **Representation**:")
        errors = check_brd.check_step_3(self.sections(text))
        self.assertTrue(any("bias and representation" in error for error in errors))

    def test_blank_ethics_response_is_reported(self):
        text = SAMPLE.replace("- **Uncertainty**: scenario values cannot establish real demand.", "- **Uncertainty**:")
        errors = check_brd.check_step_3(self.sections(text))
        self.assertTrue(any("uncertainty" in error for error in errors))

    def test_default_starter_fails_with_recovery_feedback(self):
        starter = Path(__file__).resolve().parents[1] / "docs" / "brd.md"
        sections = self.sections(starter.read_text(encoding="utf-8"))
        errors = check_brd.check_step_1(sections)
        self.assertTrue(errors)
        self.assertTrue(any("problem statement" in error for error in errors))

    def test_cli_reports_missing_file_as_error(self):
        with patch.object(
            sys,
            "argv",
            ["check_brd.py", "--all", "--file", "missing-bau5q1.md"],
        ):
            self.assertEqual(check_brd.main(), 2)


if __name__ == "__main__":
    unittest.main()
