#!/usr/bin/env python3
"""Validate the Module 2 SQLite schema, synthetic fixture, and query exercises."""

from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path
from typing import Iterable


TABLE_COLUMNS = {
    "surveys": {"survey_id", "scenario_date", "source_label"},
    "programs": {"program_id", "program_name", "program_category"},
    "program_preferences": {"survey_id", "program_id", "interest_score"},
    "venues": {"venue_id", "venue_label", "capacity"},
    "events": {"event_id", "program_id", "venue_id", "scenario_date"},
    "attendance": {"event_id", "scenario_registered_count", "scenario_attended_count"},
    "expenses": {"expense_id", "event_id", "expense_category", "estimated_amount_usd"},
}
PRIMARY_KEYS = {
    "surveys": {"survey_id"},
    "programs": {"program_id"},
    "program_preferences": {"survey_id", "program_id"},
    "venues": {"venue_id"},
    "events": {"event_id"},
    "attendance": {"event_id"},
    "expenses": {"expense_id"},
}
FOREIGN_KEYS = {
    ("program_preferences", "survey_id", "surveys", "survey_id"),
    ("program_preferences", "program_id", "programs", "program_id"),
    ("events", "program_id", "programs", "program_id"),
    ("events", "venue_id", "venues", "venue_id"),
    ("attendance", "event_id", "events", "event_id"),
    ("expenses", "event_id", "events", "event_id"),
}
FORBIDDEN_COLUMN_WORDS = re.compile(
    (
        r"(?:^|_)(?:"
        r"email|phone|mobile|contact|address|religion|religious|faith|affiliation|"
        r"respondent|member|person|individual|full|first|last"
        r")_?(?:name)?(?:_|$)"
    ),
    re.IGNORECASE,
)
EXPECTED_COUNTS = {
    "surveys": 5,
    "programs": 4,
    "program_preferences": 10,
    "venues": 3,
    "events": 5,
    "attendance": 5,
    "expenses": 10,
}
EXPECTED_ROWS = {
    "surveys": [
        (f"S00{index}", "2030-01-01", "synthetic") for index in range(1, 6)
    ],
    "programs": [
        ("P1", "Cultural learning", "education"),
        ("P2", "Celebration gathering", "celebration"),
        ("P3", "Community gathering", "community"),
        ("P4", "Family workshop", "education"),
    ],
    "program_preferences": [
        ("S001", "P1", 4),
        ("S002", "P1", 4),
        ("S003", "P1", 4),
        ("S001", "P2", 5),
        ("S002", "P2", 4),
        ("S003", "P2", 4),
        ("S004", "P3", 5),
        ("S005", "P3", 4),
        ("S004", "P4", 5),
        ("S005", "P4", 4),
    ],
    "venues": [
        ("V1", "Venue A", 50),
        ("V2", "Venue B", 40),
        ("V3", "Venue C", 25),
    ],
    "events": [
        ("E001", "P1", "V1", "2030-02-01"),
        ("E002", "P2", "V2", "2030-02-08"),
        ("E003", "P3", "V1", "2030-02-15"),
        ("E004", "P1", "V3", "2030-02-22"),
        ("E005", "P4", "V2", "2030-03-01"),
    ],
    "attendance": [
        ("E001", 35, 30),
        ("E002", 45, 40),
        ("E003", 30, 25),
        ("E004", 25, 20),
        ("E005", 20, 15),
    ],
    "expenses": [
        ("X001", "E001", "venue", 300.0),
        ("X002", "E001", "supplies", 200.0),
        ("X003", "E002", "venue", 500.0),
        ("X004", "E002", "supplies", 300.0),
        ("X005", "E003", "venue", 250.0),
        ("X006", "E003", "supplies", 150.0),
        ("X007", "E004", "venue", 200.0),
        ("X008", "E004", "supplies", 150.0),
        ("X009", "E005", "venue", 180.0),
        ("X010", "E005", "supplies", 120.0),
    ],
}
QUERY_FILES = {
    "preference": "01-preference-summary.sql",
    "capacity": "02-event-capacity.sql",
    "cost": "03-cost-per-attendee.sql",
    "above_average": "04-above-average-attendance.sql",
    "ranking": "05-rank-events.sql",
}
EXPECTED_QUERIES = {
    "preference": (
        ["program_id", "program_name", "preference_count", "average_interest_score"],
        [
            ("P1", "Cultural learning", 3, 4.0),
            ("P2", "Celebration gathering", 3, 4.33),
            ("P3", "Community gathering", 2, 4.5),
            ("P4", "Family workshop", 2, 4.5),
        ],
    ),
    "capacity": (
        [
            "event_id",
            "program_name",
            "venue_label",
            "scenario_attended_count",
            "capacity",
            "fill_percentage",
        ],
        [
            ("E001", "Cultural learning", "Venue A", 30, 50, 60.0),
            ("E002", "Celebration gathering", "Venue B", 40, 40, 100.0),
            ("E003", "Community gathering", "Venue A", 25, 50, 50.0),
            ("E004", "Cultural learning", "Venue C", 20, 25, 80.0),
            ("E005", "Family workshop", "Venue B", 15, 40, 37.5),
        ],
    ),
    "cost": (
        [
            "event_id",
            "scenario_attended_count",
            "estimated_total_cost_usd",
            "cost_per_attendee_usd",
        ],
        [
            ("E001", 30, 500.0, 16.67),
            ("E002", 40, 800.0, 20.0),
            ("E003", 25, 400.0, 16.0),
            ("E004", 20, 350.0, 17.5),
            ("E005", 15, 300.0, 20.0),
        ],
    ),
    "above_average": (
        ["event_id", "scenario_attended_count"],
        [("E001", 30), ("E002", 40)],
    ),
    "ranking": (
        ["program_id", "event_id", "rank_within_program"],
        [
            ("P1", "E001", 1),
            ("P1", "E004", 2),
            ("P2", "E002", 1),
            ("P3", "E003", 1),
            ("P4", "E005", 1),
        ],
    ),
}
REQUIRED_SQL = {
    "preference": {
        "tables": {"programs", "program_preferences"},
        "functions": {"avg"},
        "tokens": ("JOIN", "JOIN SURVEYS", "GROUP BY"),
    },
    "capacity": {
        "tables": {"events", "programs", "venues", "attendance"},
        "functions": set(),
        "tokens": ("JOIN",),
    },
    "cost": {
        "tables": {"attendance", "expenses"},
        "functions": {"sum"},
        "tokens": ("JOIN", "GROUP BY"),
    },
}
QUERY_PERTURBATIONS = {
    "preference": (
        "UPDATE program_preferences SET interest_score = 2 WHERE survey_id = 'S001' AND program_id = 'P1'",
        "program preference",
    ),
    "capacity": (
        "UPDATE venues SET capacity = 60 WHERE venue_id = 'V1'",
        "venue capacity",
    ),
    "cost": (
        "UPDATE expenses SET estimated_amount_usd = estimated_amount_usd + 1 WHERE expense_id = 'X001'",
        "estimated expense",
    ),
    "above_average": (
        "UPDATE attendance SET scenario_attended_count = 35 WHERE event_id = 'E001'",
        "scenario attendance",
    ),
    "ranking": (
        "UPDATE attendance SET scenario_attended_count = 50 WHERE event_id = 'E004'",
        "scenario attendance",
    ),
}
STEPS = {
    "1": (),
    "2": (),
    "3": ("preference", "capacity", "cost"),
    "4": tuple(QUERY_FILES),
    "all": tuple(QUERY_FILES),
}


class ExerciseError(Exception):
    """A learner-facing exercise validation error."""


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        raise ExerciseError(f"Could not read {path}: {error}") from error


def connect_with_schema(root: Path) -> sqlite3.Connection:
    schema = read_text(root, "sql/schema.sql")
    if "TODO" in schema.upper():
        raise ExerciseError("Replace the TODO in sql/schema.sql with the seven CREATE TABLE statements.")
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        connection.executescript(schema)
    except sqlite3.Error as error:
        connection.close()
        raise ExerciseError(f"Could not execute sql/schema.sql: {error}") from error
    return connection


def validate_schema(connection: sqlite3.Connection) -> list[str]:
    errors = []
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        errors.append("The validation database did not enable foreign-key enforcement.")

    found_tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    missing_tables = set(TABLE_COLUMNS) - found_tables
    unexpected_tables = found_tables - set(TABLE_COLUMNS)
    if missing_tables:
        errors.append(f"Create the missing tables: {', '.join(sorted(missing_tables))}.")
    if unexpected_tables:
        errors.append(f"Keep the exercise schema to the documented tables; unexpected: {', '.join(sorted(unexpected_tables))}.")

    found_foreign_keys = set()
    for table in found_tables & set(TABLE_COLUMNS):
        columns = {
            row["name"]: row
            for row in connection.execute(f'PRAGMA table_info("{table}")')
        }
        for column in columns:
            if FORBIDDEN_COLUMN_WORDS.search(column):
                errors.append(f"{table}.{column}: do not store personal or sensitive information.")
        missing_columns = TABLE_COLUMNS[table] - set(columns)
        if missing_columns:
            errors.append(f"{table}: add required columns {', '.join(sorted(missing_columns))}.")
            continue
        unexpected_columns = set(columns) - TABLE_COLUMNS[table]
        if unexpected_columns:
            errors.append(f"{table}: remove undocumented columns {', '.join(sorted(unexpected_columns))}.")
        primary_keys = {name for name, row in columns.items() if row["pk"]}
        if primary_keys != PRIMARY_KEYS[table]:
            errors.append(f"{table}: primary key should be {', '.join(sorted(PRIMARY_KEYS[table]))}.")

        for row in connection.execute(f'PRAGMA foreign_key_list("{table}")'):
            found_foreign_keys.add((table, row["from"], row["table"], row["to"]))

    missing_foreign_keys = FOREIGN_KEYS - found_foreign_keys
    for child, column, parent, parent_column in sorted(missing_foreign_keys):
        errors.append(f"Add foreign key {child}.{column} → {parent}.{parent_column}.")
    if not errors:
        try:
            errors.extend(validate_constraints(connection))
        except sqlite3.Error as error:
            errors.append(f"Could not validate schema CHECK constraints: {error}.")
    return errors


def validate_constraints(connection: sqlite3.Connection) -> list[str]:
    checks = [
        (
            "INSERT INTO surveys (survey_id, scenario_date, source_label) VALUES (?, ?, ?)",
            ("__check_survey__", "2030-01-01", "not-synthetic"),
            "surveys.source_label must identify the fixture as synthetic",
        ),
        (
            "INSERT INTO program_preferences (survey_id, program_id, interest_score) VALUES (?, ?, ?)",
            ("__check_survey__", "__check_program__", 0),
            "program_preferences.interest_score must be between 1 and 5",
        ),
        (
            "INSERT INTO program_preferences (survey_id, program_id, interest_score) VALUES (?, ?, ?)",
            ("__check_survey__", "__check_program__", 6),
            "program_preferences.interest_score must be between 1 and 5",
        ),
        (
            "INSERT INTO venues (venue_id, venue_label, capacity) VALUES (?, ?, ?)",
            ("__check_venue__", "Constraint check venue", 0),
            "venues.capacity must be positive",
        ),
        (
            "INSERT INTO attendance (event_id, scenario_registered_count, scenario_attended_count) VALUES (?, ?, ?)",
            ("__check_event__", -1, 1),
            "attendance.scenario_registered_count must be nonnegative",
        ),
        (
            "INSERT INTO attendance (event_id, scenario_registered_count, scenario_attended_count) VALUES (?, ?, ?)",
            ("__check_event__", 1, -1),
            "attendance.scenario_attended_count must be nonnegative",
        ),
        (
            "INSERT INTO expenses (expense_id, event_id, expense_category, estimated_amount_usd) VALUES (?, ?, ?, ?)",
            ("__check_expense__", "__check_event__", "validation", -1),
            "expenses.estimated_amount_usd must be nonnegative",
        ),
    ]
    connection.execute("SAVEPOINT constraint_validation")
    errors = []
    try:
        connection.execute(
            "INSERT INTO surveys (survey_id, scenario_date, source_label) VALUES (?, ?, ?)",
            ("__check_survey__", "2030-01-01", "synthetic"),
        )
        connection.execute(
            "INSERT INTO programs (program_id, program_name, program_category) VALUES (?, ?, ?)",
            ("__check_program__", "Constraint check program", "validation"),
        )
        connection.execute(
            "INSERT INTO venues (venue_id, venue_label, capacity) VALUES (?, ?, ?)",
            ("__check_venue__", "Constraint check venue", 10),
        )
        connection.execute(
            "INSERT INTO events (event_id, program_id, venue_id, scenario_date) VALUES (?, ?, ?, ?)",
            ("__check_event__", "__check_program__", "__check_venue__", "2030-01-01"),
        )
        for statement, values, description in checks:
            connection.execute("SAVEPOINT single_constraint_validation")
            try:
                connection.execute(statement, values)
            except sqlite3.IntegrityError as error:
                if "CHECK constraint failed" not in str(error):
                    errors.append(f"{description}; the rejected row failed for another reason: {error}.")
            else:
                errors.append(f"Add a CHECK constraint so {description}.")
            finally:
                connection.execute("ROLLBACK TO single_constraint_validation")
                connection.execute("RELEASE single_constraint_validation")
    finally:
        connection.execute("ROLLBACK TO constraint_validation")
        connection.execute("RELEASE constraint_validation")
    return errors


def validate_seed(connection: sqlite3.Connection, root: Path) -> list[str]:
    seed = read_text(root, "sql/seed.sql")
    if "TODO" in seed.upper():
        return ["Replace the TODO in sql/seed.sql with the fixed synthetic fixture."]
    try:
        connection.executescript(seed)
    except sqlite3.Error as error:
        return [f"Could not load sql/seed.sql: {error}"]

    errors = []
    for table, expected_count in EXPECTED_COUNTS.items():
        actual_count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        if actual_count != expected_count:
            errors.append(f"{table}: expected {expected_count} synthetic rows, found {actual_count}.")
        expected_rows = sorted(normalize_row(row) for row in EXPECTED_ROWS[table])
        actual_rows = sorted(
            normalize_row(row)
            for row in connection.execute(f'SELECT * FROM "{table}"')
        )
        if actual_rows != expected_rows:
            errors.append(
                f"{table}: values must match the documented synthetic fixture; "
                "check IDs, scenario dates, labels, scores, capacities, and estimates."
            )
    violations = connection.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        errors.append(f"Foreign-key check found {len(violations)} violation(s); verify parent IDs and insert order.")
    invalid_scores = connection.execute(
        "SELECT COUNT(*) FROM program_preferences WHERE interest_score NOT BETWEEN 1 AND 5"
    ).fetchone()[0]
    if invalid_scores:
        errors.append("program_preferences: interest scores must be integers from 1 through 5.")
    over_capacity = connection.execute(
        """
        SELECT COUNT(*)
        FROM attendance AS a
        JOIN events AS e USING (event_id)
        JOIN venues AS v USING (venue_id)
        WHERE a.scenario_attended_count > v.capacity
        """
    ).fetchone()[0]
    if over_capacity:
        errors.append("Attendance scenario exceeds venue capacity; correct the fixture or explain a deliberate over-capacity scenario.")
    return errors


def normalize_row(row: Iterable[object]) -> tuple[object, ...]:
    return tuple(round(value, 2) if isinstance(value, float) else value for value in row)


def executable_sql(sql: str) -> str:
    without_comments = re.sub(r"/\*.*?\*/|--[^\r\n]*", " ", sql, flags=re.DOTALL)
    return re.sub(r"'(?:''|[^'])*'", "''", without_comments)


def inspect_query(
    connection: sqlite3.Connection,
    sql: str,
) -> tuple[list[str], list[tuple[object, ...]], set[str], set[str]]:
    seen_tables = set()
    seen_functions = set()

    def authorizer(action, argument1, argument2, _database, _source):
        if action == sqlite3.SQLITE_READ:
            seen_tables.add(argument1.lower())
        elif action == sqlite3.SQLITE_FUNCTION and argument2:
            seen_functions.add(argument2.lower())
        return sqlite3.SQLITE_OK

    connection.set_authorizer(authorizer)
    try:
        cursor = connection.execute(sql)
        columns = [description[0] for description in cursor.description or ()]
        rows = sorted(normalize_row(row) for row in cursor.fetchall())
    finally:
        connection.set_authorizer(None)
    return columns, rows, seen_tables, seen_functions


def query_requirements_met(
    name: str,
    sql: str,
    seen_tables: set[str],
    seen_functions: set[str],
) -> bool:
    upper_sql = executable_sql(sql).upper()
    if name in REQUIRED_SQL:
        requirements = REQUIRED_SQL[name]
        if not requirements["tables"].issubset(seen_tables):
            return False
        if not requirements["functions"].issubset(seen_functions):
            return False
        if not all(token in upper_sql for token in requirements["tokens"]):
            return False
    if name == "above_average":
        return (
            upper_sql.count("SELECT") >= 2
            and "AVG(" in upper_sql
            and "avg" in seen_functions
            and "WHERE" in upper_sql
            and "attendance" in seen_tables
        )
    if name == "ranking":
        return (
            bool(re.search(r"\bWITH\b", upper_sql))
            and bool(re.search(r"ROW_NUMBER\s*\(\s*\)\s*OVER", upper_sql))
            and bool(re.search(r"\bPARTITION\s+BY\b", upper_sql))
            and "row_number" in seen_functions
            and {"events", "attendance"}.issubset(seen_tables)
        )
    return True


def validate_query(
    connection: sqlite3.Connection,
    root: Path,
    name: str,
) -> list[str]:
    relative_path = f"sql/queries/{QUERY_FILES[name]}"
    try:
        sql = read_text(root, relative_path)
    except ExerciseError as error:
        return [str(error)]
    if "TODO" in sql.upper():
        return [f"{relative_path}: replace the TODO with a query."]
    try:
        actual_columns, actual_rows, seen_tables, seen_functions = inspect_query(connection, sql)
    except sqlite3.Error as error:
        return [f"{relative_path}: query failed: {error}"]
    if not query_requirements_met(name, sql, seen_tables, seen_functions):
        return [f"{relative_path}: use the required tables and SQL technique in executable query logic, not comments or hard-coded output."]

    expected_columns, expected_rows = EXPECTED_QUERIES[name]
    if actual_columns != expected_columns:
        return [
            f"{relative_path}: expected result columns {expected_columns}, found {actual_columns}."
        ]
    normalized_expected = sorted(normalize_row(row) for row in expected_rows)
    if actual_rows != normalized_expected:
        return [
            f"{relative_path}: results do not match the documented synthetic fixture; "
            "check joins, grouping, filters, and calculation grain."
        ]
    mutation, changed_input = QUERY_PERTURBATIONS[name]
    connection.execute("SAVEPOINT query_sensitivity_check")
    try:
        connection.execute(mutation)
        _, changed_rows, _, _ = inspect_query(connection, sql)
    except sqlite3.Error as error:
        return [f"{relative_path}: could not verify that results respond to {changed_input}: {error}"]
    finally:
        connection.execute("ROLLBACK TO query_sensitivity_check")
        connection.execute("RELEASE query_sensitivity_check")
    if changed_rows == actual_rows:
        return [f"{relative_path}: results must respond to changes in the underlying {changed_input} data."]
    return []


def validate(root: Path, step: str) -> list[str]:
    try:
        connection = connect_with_schema(root)
    except ExerciseError as error:
        return [str(error)]
    try:
        errors = validate_schema(connection)
        if errors or step == "1":
            return errors

        seed_errors = validate_seed(connection, root)
        if seed_errors:
            return seed_errors
        query_errors = []
        for name in STEPS[step]:
            query_errors.extend(validate_query(connection, root, name))
        return query_errors
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--step", choices=tuple(STEPS))
    selection.add_argument("--all", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."), help="Exercise root directory")
    args = parser.parse_args()
    step = "all" if args.all else args.step

    errors = validate(args.root, step)
    if errors:
        print("Not quite yet — review these items:")
        for error in errors:
            print(f"- {error}")
        return 1

    label = "all SQL checks" if step == "all" else f"step {step}"
    print(f"Great work: {label} passed for {args.root}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
