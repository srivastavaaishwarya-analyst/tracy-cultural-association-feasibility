## Module 2, Step 3: Answer business questions with joins and aggregates

Use the synthetic fixture to compare program preferences, event capacity, and estimated costs. Be deliberate about how many rows each join creates so event attendance is not accidentally counted once per expense line.

### 📖 Theory: Join at the right grain

A join combines related tables, while `GROUP BY` summarizes records at a chosen business grain such as program or event. Joining one attendance row directly to multiple expense rows can duplicate attendance, so query design must account for row multiplicity. These summaries compare scenarios; they do not estimate real demand.

### ⌨️ Activity: Summarize preferences, capacity, and costs

1. Complete `sql/queries/01-preference-summary.sql` with joins and aggregation to report preference count and average interest by program.
2. Complete `sql/queries/02-event-capacity.sql` to report scenario attendance, venue capacity, and fill percentage by event.
3. Complete `sql/queries/03-cost-per-attendee.sql` to summarize estimated expenses and scenario cost per attendee without double-counting.
4. Run the core-query validator.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > python3 scripts/check_sql_exercise.py --step 3
   > ```

<details>
<summary>Having trouble? 🤷</summary><br/>

- Compare row counts before and after each join.
- Aggregate expenses before joining if needed.
- Handle division by zero with a deliberate rule.

</details>
