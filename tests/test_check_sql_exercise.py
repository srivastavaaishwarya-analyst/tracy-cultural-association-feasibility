import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "check_sql_exercise.py"
SPEC = importlib.util.spec_from_file_location("check_sql_exercise", MODULE_PATH)
check_sql_exercise = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_sql_exercise)


SCHEMA = """
CREATE TABLE surveys (
    survey_id TEXT PRIMARY KEY,
    scenario_date TEXT NOT NULL,
    source_label TEXT NOT NULL CHECK (source_label = 'synthetic')
);
CREATE TABLE programs (
    program_id TEXT PRIMARY KEY,
    program_name TEXT NOT NULL,
    program_category TEXT NOT NULL
);
CREATE TABLE program_preferences (
    survey_id TEXT NOT NULL REFERENCES surveys(survey_id),
    program_id TEXT NOT NULL REFERENCES programs(program_id),
    interest_score INTEGER NOT NULL CHECK (interest_score BETWEEN 1 AND 5),
    PRIMARY KEY (survey_id, program_id)
);
CREATE TABLE venues (
    venue_id TEXT PRIMARY KEY,
    venue_label TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0)
);
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    program_id TEXT NOT NULL REFERENCES programs(program_id),
    venue_id TEXT NOT NULL REFERENCES venues(venue_id),
    scenario_date TEXT NOT NULL
);
CREATE TABLE attendance (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    scenario_registered_count INTEGER NOT NULL CHECK (scenario_registered_count >= 0),
    scenario_attended_count INTEGER NOT NULL CHECK (scenario_attended_count >= 0)
);
CREATE TABLE expenses (
    expense_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL REFERENCES events(event_id),
    expense_category TEXT NOT NULL,
    estimated_amount_usd REAL NOT NULL CHECK (estimated_amount_usd >= 0)
);
"""

SEED = """
INSERT INTO surveys VALUES
    ('S001', '2030-01-01', 'synthetic'),
    ('S002', '2030-01-01', 'synthetic'),
    ('S003', '2030-01-01', 'synthetic'),
    ('S004', '2030-01-01', 'synthetic'),
    ('S005', '2030-01-01', 'synthetic');
INSERT INTO programs VALUES
    ('P1', 'Cultural learning', 'education'),
    ('P2', 'Celebration gathering', 'celebration'),
    ('P3', 'Community gathering', 'community'),
    ('P4', 'Family workshop', 'education');
INSERT INTO program_preferences VALUES
    ('S001', 'P1', 4), ('S002', 'P1', 4), ('S003', 'P1', 4),
    ('S001', 'P2', 5), ('S002', 'P2', 4), ('S003', 'P2', 4),
    ('S004', 'P3', 5), ('S005', 'P3', 4),
    ('S004', 'P4', 5), ('S005', 'P4', 4);
INSERT INTO venues VALUES
    ('V1', 'Venue A', 50), ('V2', 'Venue B', 40), ('V3', 'Venue C', 25);
INSERT INTO events VALUES
    ('E001', 'P1', 'V1', '2030-02-01'),
    ('E002', 'P2', 'V2', '2030-02-08'),
    ('E003', 'P3', 'V1', '2030-02-15'),
    ('E004', 'P1', 'V3', '2030-02-22'),
    ('E005', 'P4', 'V2', '2030-03-01');
INSERT INTO attendance VALUES
    ('E001', 35, 30), ('E002', 45, 40), ('E003', 30, 25),
    ('E004', 25, 20), ('E005', 20, 15);
INSERT INTO expenses VALUES
    ('X001', 'E001', 'venue', 300), ('X002', 'E001', 'supplies', 200),
    ('X003', 'E002', 'venue', 500), ('X004', 'E002', 'supplies', 300),
    ('X005', 'E003', 'venue', 250), ('X006', 'E003', 'supplies', 150),
    ('X007', 'E004', 'venue', 200), ('X008', 'E004', 'supplies', 150),
    ('X009', 'E005', 'venue', 180), ('X010', 'E005', 'supplies', 120);
"""

QUERIES = {
    "01-preference-summary.sql": """
        SELECT p.program_id, p.program_name, COUNT(pp.survey_id) AS preference_count,
               ROUND(AVG(pp.interest_score), 2) AS average_interest_score
        FROM programs AS p
        JOIN program_preferences AS pp USING (program_id)
        JOIN surveys AS s USING (survey_id)
        GROUP BY p.program_id, p.program_name
        ORDER BY p.program_id;
    """,
    "02-event-capacity.sql": """
        SELECT e.event_id, p.program_name, v.venue_label, a.scenario_attended_count,
               v.capacity,
               ROUND(100.0 * a.scenario_attended_count / v.capacity, 2) AS fill_percentage
        FROM events AS e
        JOIN programs AS p USING (program_id)
        JOIN venues AS v USING (venue_id)
        JOIN attendance AS a USING (event_id)
        ORDER BY e.event_id;
    """,
    "03-cost-per-attendee.sql": """
        WITH event_costs AS (
            SELECT event_id, SUM(estimated_amount_usd) AS estimated_total_cost_usd
            FROM expenses
            GROUP BY event_id
        )
        SELECT a.event_id, a.scenario_attended_count, c.estimated_total_cost_usd,
               ROUND(c.estimated_total_cost_usd / a.scenario_attended_count, 2)
                   AS cost_per_attendee_usd
        FROM attendance AS a
        JOIN event_costs AS c USING (event_id)
        ORDER BY a.event_id;
    """,
    "04-above-average-attendance.sql": """
        SELECT event_id, scenario_attended_count
        FROM attendance
        WHERE scenario_attended_count > (
            SELECT AVG(scenario_attended_count) FROM attendance
        )
        ORDER BY event_id;
    """,
    "05-rank-events.sql": """
        WITH ranked_events AS (
            SELECT e.program_id, a.event_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY e.program_id
                       ORDER BY a.scenario_attended_count DESC, a.event_id
                   ) AS rank_within_program
            FROM events AS e
            JOIN attendance AS a USING (event_id)
        )
        SELECT program_id, event_id, rank_within_program
        FROM ranked_events
        ORDER BY program_id, rank_within_program;
    """,
}


class CheckSqlExerciseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "sql" / "queries").mkdir(parents=True)
        (self.root / "sql" / "schema.sql").write_text(SCHEMA, encoding="utf-8")
        (self.root / "sql" / "seed.sql").write_text(SEED, encoding="utf-8")
        for filename, query in QUERIES.items():
            (self.root / "sql" / "queries" / filename).write_text(query, encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_complete_fixture_and_queries_pass(self):
        self.assertEqual(check_sql_exercise.validate(self.root, "all"), [])

    def test_starter_schema_fails_with_actionable_feedback(self):
        (self.root / "sql" / "schema.sql").write_text("-- TODO: define tables\n", encoding="utf-8")
        errors = check_sql_exercise.validate(self.root, "1")
        self.assertTrue(any("Replace the TODO" in error for error in errors))

    def test_seed_row_count_is_checked(self):
        seed = SEED.replace(
            "('E004', 25, 20), ('E005', 20, 15);",
            "('E004', 25, 20);",
        )
        (self.root / "sql" / "seed.sql").write_text(seed, encoding="utf-8")
        errors = check_sql_exercise.validate(self.root, "2")
        self.assertTrue(any("attendance: expected 5 synthetic rows, found 4" in error for error in errors))

    def test_same_count_seed_mutation_is_rejected(self):
        seed = SEED.replace("('S001', 'P1', 4)", "('S001', 'P1', 3)")
        (self.root / "sql" / "seed.sql").write_text(seed, encoding="utf-8")
        errors = check_sql_exercise.validate(self.root, "2")
        self.assertTrue(
            any("program_preferences: values must match" in error for error in errors)
        )

    def test_interest_score_constraint_is_checked_by_behavior(self):
        schema = SCHEMA.replace(
            "CHECK (interest_score BETWEEN 1 AND 5)",
            "CHECK (interest_score >= 0)",
        )
        (self.root / "sql" / "schema.sql").write_text(schema, encoding="utf-8")
        connection = check_sql_exercise.connect_with_schema(self.root)
        try:
            errors = check_sql_exercise.validate_schema(connection)
        finally:
            connection.close()
        self.assertTrue(any("interest_score must be between 1 and 5" in error for error in errors))

    def test_sensitive_column_is_rejected(self):
        schema = SCHEMA.replace("source_label TEXT NOT NULL CHECK (source_label = 'synthetic')", "religious_affiliation TEXT NOT NULL")
        (self.root / "sql" / "schema.sql").write_text(schema, encoding="utf-8")
        connection = check_sql_exercise.connect_with_schema(self.root)
        try:
            errors = check_sql_exercise.validate_schema(connection)
        finally:
            connection.close()
        self.assertTrue(any("do not store personal or sensitive information" in error for error in errors))

    def test_undocumented_column_is_rejected(self):
        schema = SCHEMA.replace(
            "source_label TEXT NOT NULL CHECK (source_label = 'synthetic')",
            "source_label TEXT NOT NULL CHECK (source_label = 'synthetic'), freeform_notes TEXT",
        )
        (self.root / "sql" / "schema.sql").write_text(schema, encoding="utf-8")
        connection = check_sql_exercise.connect_with_schema(self.root)
        try:
            errors = check_sql_exercise.validate_schema(connection)
        finally:
            connection.close()
        self.assertTrue(any("remove undocumented columns freeform_notes" in error for error in errors))

    def test_query_results_are_checked_against_fixture(self):
        query_path = self.root / "sql" / "queries" / "01-preference-summary.sql"
        query_path.write_text(
            QUERIES["01-preference-summary.sql"].replace(
                "JOIN surveys AS s USING (survey_id)",
                "JOIN surveys AS s USING (survey_id) WHERE s.survey_id != 'S001'",
            ),
            encoding="utf-8",
        )
        errors = check_sql_exercise.validate(self.root, "3")
        self.assertTrue(
            any("results do not match" in error for error in errors)
            or any("respond to changes" in error for error in errors)
        )

    def test_query_must_use_expected_sql_technique(self):
        query_path = self.root / "sql" / "queries" / "05-rank-events.sql"
        query_path.write_text("SELECT 'not ranked' AS value;", encoding="utf-8")
        errors = check_sql_exercise.validate(self.root, "4")
        self.assertTrue(any("executable query logic" in error for error in errors))

    def test_comments_and_hard_coded_rows_do_not_satisfy_query_requirements(self):
        query_path = self.root / "sql" / "queries" / "01-preference-summary.sql"
        literal_rows = "\nUNION ALL\n".join(
            f"SELECT '{program_id}' AS program_id, '{program_name}' AS program_name, "
            f"{count} AS preference_count, {score} AS average_interest_score"
            for program_id, program_name, count, score in check_sql_exercise.EXPECTED_QUERIES[
                "preference"
            ][1]
        )
        query_path.write_text(
            f"-- JOIN programs, JOIN surveys, GROUP BY, AVG(interest_score)\n{literal_rows};",
            encoding="utf-8",
        )
        errors = check_sql_exercise.validate(self.root, "3")
        self.assertTrue(any("executable query logic" in error for error in errors))

    def test_query_must_respond_to_underlying_data_changes(self):
        query_path = self.root / "sql" / "queries" / "01-preference-summary.sql"
        query_path.write_text(
            """
            SELECT p.program_id, p.program_name, COUNT(pp.survey_id) AS preference_count,
                   CASE p.program_id
                       WHEN 'P1' THEN 4.0 WHEN 'P2' THEN 4.33
                       WHEN 'P3' THEN 4.5 WHEN 'P4' THEN 4.5 END
                       + AVG(pp.interest_score) * 0 AS average_interest_score
            FROM programs AS p
            JOIN program_preferences AS pp USING (program_id)
            JOIN surveys AS s USING (survey_id)
            GROUP BY p.program_id, p.program_name
            ORDER BY p.program_id;
            """,
            encoding="utf-8",
        )
        errors = check_sql_exercise.validate(self.root, "3")
        self.assertTrue(any("respond to changes" in error for error in errors))

    def test_missing_schema_file_is_reported(self):
        (self.root / "sql" / "schema.sql").unlink()
        errors = check_sql_exercise.validate(self.root, "1")
        self.assertTrue(any("Could not read" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
