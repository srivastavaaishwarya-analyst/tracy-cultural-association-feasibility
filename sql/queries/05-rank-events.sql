-- Return program_id, event_id, and rank_within_program.
-- Rank by scenario_attended_count descending, then event_id for deterministic ties.

-- TODO: Use a CTE and ROW_NUMBER() OVER (PARTITION BY ...).
