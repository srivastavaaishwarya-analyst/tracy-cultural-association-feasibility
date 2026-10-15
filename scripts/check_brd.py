#!/usr/bin/env python3
"""Give step-specific feedback on the learner's BRD without external packages."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


DEFAULT_FILE = Path("docs/brd.md")
SECTION_PATTERN = re.compile(r"^## (?P<title>\d+)\. (?P<name>.+)$", re.MULTILINE)
PLACEHOLDERS = re.compile(
    r"\bTODO\b|write your|identify the|list evidence|explain how|state what",
    re.IGNORECASE,
)


def read_sections(text: str) -> dict[str, str]:
    """Return numbered BRD sections keyed by their heading name."""
    matches = list(SECTION_PATTERN.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group("name").strip().lower()] = text[match.end() : end]
    return sections


def section_text(sections: dict[str, str], name: str) -> str:
    """Return one named section or an empty string when it is missing."""
    return sections.get(name.lower(), "")


def has_learner_content(text: str) -> bool:
    """Require meaningful prose and reject starter prompts and template cells."""
    cleaned = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"`[^`]*`", "", cleaned)
    lines = [
        line.strip()
        for line in cleaned.splitlines()
        if line.strip() and not line.lstrip().startswith((">", "#", "|---", "| ---"))
    ]
    substantive = [line for line in lines if not re.fullmatch(r"\|?[\s|:-]*\|?", line)]
    return bool(substantive) and not PLACEHOLDERS.search("\n".join(substantive))


def table_rows(text: str) -> list[list[str]]:
    """Parse Markdown table data rows, excluding headers and separators."""
    rows = []
    header_seen = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"[\s:-]*", cell) for cell in cells):
            continue
        if not header_seen:
            header_seen = True
            continue
        if any(not cell for cell in cells):
            continue
        if any(re.fullmatch(r"[\s-]*TODO[\s-]*:?.*", cell, re.IGNORECASE) for cell in cells):
            continue
        if any("TODO" in cell.upper() for cell in cells):
            continue
        rows.append(cells)
    return rows


def check_step_1(sections: dict[str, str]) -> list[str]:
    errors = []
    problem = section_text(sections, "problem statement")
    if not has_learner_content(problem):
        errors.append("Section 1: write a specific problem statement without TODOs.")
    stakeholders = section_text(sections, "decision owner and stakeholders")
    owner_match = re.search(
        r"^### Decision owner\s*$([\s\S]*?)(?=^### Stakeholders\s*$|\Z)",
        stakeholders,
        re.MULTILINE,
    )
    if not owner_match or not has_learner_content(owner_match.group(1)):
        errors.append("Section 2: name a decision-owner role and describe stakeholder needs.")
    stakeholder_match = re.search(
        r"^### Stakeholders\s*$([\s\S]*)\Z",
        stakeholders,
        re.MULTILINE,
    )
    roles = table_rows(stakeholder_match.group(1)) if stakeholder_match else []
    if len(roles) < 2:
        errors.append("Section 2: add at least two stakeholder roles with decision needs.")
    return errors


def check_step_2(sections: dict[str, str]) -> list[str]:
    errors = []
    objectives = section_text(sections, "objectives")
    objective_lines = [
        line for line in objectives.splitlines()
        if re.match(r"^\s*[-*]\s+", line) and has_learner_content(line)
    ]
    if len(objective_lines) < 2:
        errors.append("Section 3: write at least two measurable objectives.")

    scope = section_text(sections, "scope and non-goals")
    for label in ("### In scope", "### Out of scope"):
        match = re.search(
            rf"^{re.escape(label)}\s*$([\s\S]*?)(?=^### |\Z)",
            scope,
            re.MULTILINE,
        )
        if not match or not has_learner_content(match.group(1)):
            errors.append(f"Section 4: add learner-written content under {label[4:].lower()}.")

    assumptions = section_text(sections, "assumptions and evidence plan")
    assumption_rows = table_rows(assumptions)
    if len(assumption_rows) < 2:
        errors.append("Section 5: add at least two assumptions with status and verification plan.")
    else:
        for row in assumption_rows:
            if len(row) < 3:
                errors.append("Section 5: each assumption row needs status and verification-plan columns.")
                break
            if not re.search(r"\bhypothetical\b|\bverified\b", row[1], re.IGNORECASE):
                errors.append("Section 5: label each assumption status as hypothetical or verified.")
                break
    return errors


def check_step_3(sections: dict[str, str]) -> list[str]:
    errors = []
    for section_name, prefix in (
        ("functional requirements", "FR-"),
        ("nonfunctional requirements", "NFR-"),
    ):
        section = section_text(sections, section_name)
        rows = table_rows(section)
        if not rows:
            errors.append(f"Section {6 if prefix == 'FR-' else 7}: add at least one {section_name} row.")
            continue
        if len(rows[0]) < 3 or not rows[0][0].startswith(prefix):
            errors.append(f"Section {6 if prefix == 'FR-' else 7}: include an ID, requirement, and evidence.")

    kpis = table_rows(section_text(sections, "success metrics and decision kpis"))
    if len(kpis) < 2:
        errors.append("Section 8: define at least two KPIs with definition, unit, evidence, and proposed threshold.")
    else:
        for row in kpis:
            if len(row) < 4:
                errors.append("Section 8: each KPI row needs a definition/unit, evidence, and proposed threshold.")
                break
            if not any(
                re.search(r"\b(propos\w*|hypothetical|not yet|placeholder)\b", cell, re.IGNORECASE)
                for cell in row[3:]
            ):
                errors.append("Section 8: label each threshold as a proposal, not an established fact.")
                break

    ethics = section_text(sections, "risks, ethics, and limitations")
    for label in ("Bias and representation", "Uncertainty", "Responsible use"):
        match = re.search(
            rf"^[ \t]*[-*][ \t]+\*\*{re.escape(label)}\*\*[ \t]*:[ \t]*(.+?)[ \t]*$",
            ethics,
            re.MULTILINE | re.IGNORECASE,
        )
        if not match or not has_learner_content(match.group(1)):
            errors.append(f"Section 9: add meaningful learner-written content for {label.lower()}.")
    return errors


def check_all(sections: dict[str, str]) -> list[str]:
    errors = check_step_1(sections) + check_step_2(sections) + check_step_3(sections)
    open_questions = section_text(sections, "open questions")
    if not has_learner_content(open_questions):
        errors.append("Section 10: replace the TODO with an evidence need or explain what remains open.")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--step", choices=("1", "2", "3", "4"))
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--file", type=Path, default=DEFAULT_FILE, help="BRD Markdown file to check")
    args = parser.parse_args()

    try:
        text = args.file.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Could not read {args.file}: {error}", file=sys.stderr)
        return 2

    sections = read_sections(text)
    checks = {
        "1": check_step_1,
        "2": check_step_2,
        "3": check_step_3,
        "4": check_all,
    }
    errors = check_all(sections) if args.all else checks[args.step](sections)
    if errors:
        print("Not quite yet — review these items:")
        for error in errors:
            print(f"- {error}")
        return 1

    label = "all BRD checks" if args.all else f"step {args.step}"
    print(f"Great work: {label} passed for {args.file}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
