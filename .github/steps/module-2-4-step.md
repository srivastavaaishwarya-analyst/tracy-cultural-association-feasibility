## Module 2, Step 4: Use subqueries, a CTE, and a window function

Extend the analysis with comparisons and rankings, then review the schema, synthetic data, and query logic in a pull request. Use advanced SQL only where it makes the business question clearer.

### 📖 Theory: Compare and rank without hiding logic

A subquery can compare an event with an overall summary, while a common table expression (CTE) gives a calculation a readable name. A window function ranks rows within groups without collapsing detail rows, which is useful when comparing events within each program. These techniques complement simple counts and averages; they should not replace a simpler aggregate when that is enough.

### ⌨️ Activity: Extend and review the analysis

1. Complete `sql/queries/04-above-average-attendance.sql` to find events above the overall scenario-attendance mean of 26.
2. Complete `sql/queries/05-rank-events.sql` using a CTE and `ROW_NUMBER()` to rank events within each program.
3. Run the complete SQL validator.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > python3 scripts/check_sql_exercise.py --all
   > ```

4. Run the validator tests.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > python3 -m unittest discover -s tests -v
   > ```

5. Open a pull request with your schema, seed data, and queries. Describe one join-grain decision and one limitation of synthetic data.

<details>
<summary>Having trouble? 🤷</summary><br/>

- Use a CTE to make the overall mean explicit.
- Add a deterministic tie-breaker to the window ordering.
- Check that query outputs keep one row per event.

</details>
