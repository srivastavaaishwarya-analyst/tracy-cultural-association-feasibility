## Module 2, Step 2: Load and validate synthetic data

With the relationships in place, add a small fixed dataset that lets every learner reproduce the same query results. The records are fictional scenario inputs, not observations about real people or events.

### 📖 Theory: Referential integrity and data quality

A database can contain plausible-looking rows that refer to missing parent records or violate business rules. Foreign-key checks and row-count assertions expose those errors before a query silently drops records. Because every record here is synthetic, counts and amounts are reproducible exercise fixtures—not evidence of real demand or costs.

### ⌨️ Activity: Seed the database

1. Add the synthetic records to `sql/seed.sql`, matching the documented fixture counts.
2. Run the seed-data validator.

   > ![Static Badge](https://img.shields.io/badge/Terminal-text?logo=gnometerminal&labelColor=0969da&color=ddf4ff)
   >
   > ```bash
   > python3 scripts/check_sql_exercise.py --step 2
   > ```

3. Review row counts and integrity results. Fix rejected records instead of disabling constraints.

<details>
<summary>Having trouble? 🤷</summary><br/>

- Insert parent records before child records.
- Check foreign-key IDs and score/count ranges.
- Keep every value labeled synthetic or scenario-estimated.

</details>
