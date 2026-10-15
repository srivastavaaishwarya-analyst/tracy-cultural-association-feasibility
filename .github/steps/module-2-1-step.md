## Module 2, Step 1: Model the relational data

Stakeholders need a reproducible way to compare hypothetical program preferences, venue capacity, scenario attendance, and estimated expenses. Start by representing each kind of fact once and connecting related records with keys.

### 📖 Theory: Tables and relationships

Relational design stores each kind of fact once and links related records with keys, which reduces update errors and makes analyses traceable. A survey preference belongs to both a survey record and a program; an event connects a program with a venue; attendance and expenses belong to an event. Primary keys, foreign keys, and check constraints catch invalid records before they distort business summaries.

### ⌨️ Activity: Create the schema

1. Create a feature branch and inspect the incomplete `sql/schema.sql` starter.
2. Define the seven tables, primary/foreign keys, and checks for nonnegative counts and scores and valid interest-score ranges.
3. Run the schema validator.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > python3 scripts/check_sql_exercise.py --step 1
   > ```

<details>
<summary>Having trouble? 🤷</summary><br/>

- SQLite foreign keys must be enabled by the exercise runner.
- Use the table and column names in the starter comments.
- Keep personally identifying and religious-affiliation fields out of the design.

</details>
