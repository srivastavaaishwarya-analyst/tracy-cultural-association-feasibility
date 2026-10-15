# Feasibility Analysis of Establishing a Hindu Cultural Association in Tracy, California

Build a transparent, hypothetical decision-support analysis through a guided, self-paced business analytics project.

## Welcome

- **Who is this for**: Business analytics learners who are new to GitHub-based projects and want to progress from requirements to intermediate analysis.
- **What you'll learn**: Frame a decision, design relational data, query with SQL, explore data with Python, analyze scenarios, evaluate a simple predictive model, and communicate recommendations.
- **What you'll build**: A reproducible portfolio project that compares whether to pilot, proceed, or gather more evidence about a hypothetical cultural association.
- **Prerequisites**:
  - A GitHub account and browser.
  - Curiosity; the first module does not require programming.
- **How long**: Module 1 takes about 45–60 minutes; Module 2 takes about 90–120 minutes. The complete journey is self-paced.

This repository is a learning experience, not a claim that a real association or demand study exists. Use synthetic data and label every scenario assumption. Do not infer local religious affiliation, identify individuals, or present hypothetical figures as facts. Any future real-world claim must cite a verified source and document its permitted use.

### Learning journey

The planned sequence is:

1. **Business requirements** — frame the decision and document stakeholders, scope, assumptions, safeguards, and success metrics.
2. **Data and SQL** — model synthetic survey, event, attendance, expense, venue, and program-preference data; practice joins, aggregations, subqueries, CTEs, and window functions.
3. **Python and EDA** — import, validate, clean, and visualize data with pandas, NumPy, and matplotlib.
4. **Business analytics** — compare hypothetical demand, attendance, capacity, costs, and revenue transparently.
5. **Machine learning** — build and evaluate a modest scikit-learn baseline only where prediction adds value; explain limitations.
6. **Decision analysis** — compare transparent scenarios under budget, capacity, and program constraints.
7. **Dashboard and recommendations** — present demand, forecasts, costs, and scenarios in Streamlit.
8. **Portfolio documentation** — complete architecture, data dictionary, ER diagram, setup, testing plan, and presentation outline.

Modules 1 and 2 are available as separate guided exercises. Modules 3–8 are roadmap items, not completed materials.

## Module 1: Frame the Feasibility Decision

In this exercise, you will:

1. Identify the decision, owner, and stakeholder needs.
2. Bound the objectives, scope, non-goals, and hypothetical assumptions.
3. Define testable requirements, safeguards, and decision KPIs.
4. Review your BRD in a pull request and respond to automated feedback.

The deliverable is `docs/brd.md`. Starter prompts are intentionally incomplete: write your own analysis rather than copying a completed answer.

### How to start this exercise

Use the **Copy Exercise** button to create your learner repository. After the copy completes, the `Step 0` workflow creates the exercise issue and posts the first lesson. The source repository's start workflow is guarded so it will not create a learner issue here.

[![Copy Exercise](https://img.shields.io/badge/Copy%20Exercise-%E2%86%92-1f883d?style=for-the-badge&logo=github&labelColor=197935)](https://github.com/new?template_owner=srivastavaaishwarya-analyst&template_name=tracy-cultural-association-feasibility&owner=%40me&name=tracy-cultural-association-feasibility&description=Exercise%3A%20Frame%20the%20Feasibility%20Decision&visibility=public)

If the `Step 0` workflow fails, first check whether it already created the exercise issue. If it did not, open **Issues → New issue → Exercise recovery: Start Module 1** and submit the form. The recovery workflow posts Step 1 and enables its grader. Check the Actions tab for the failed run and its error before retrying.

## Module 2: Model the Decision Data and Query Scenarios

After Module 1's final review completes, **Module 2 Start** is enabled in your copied repository. Open **Actions → Module 2 Start → Run workflow** once to create a separate issue titled **Exercise: Module 2 - Model the Decision Data and Query Scenarios**. The lesson sequence models synthetic surveys, program preferences, venues, events, attendance, and estimated expenses with SQLite; then it uses joins, aggregations, a subquery, a CTE, and a window function.

All records are synthetic fixtures, not facts about Tracy or real community members. Module 2 uses Python's standard-library `sqlite3`; no database server or package installation is needed.

## Validation and support

Each lesson has a GitHub Actions check that validates a specific part of your work. Module 1 checks the BRD; Module 2 checks the schema, seed fixture, and query outputs. A structural pass does not mean stakeholders have approved hypothetical assumptions; use the PR review to identify unresolved questions.

Run checks locally from the repository root:

```bash
python3 scripts/check_brd.py --step 1
python3 scripts/check_brd.py --step 2
python3 scripts/check_brd.py --step 3
python3 scripts/check_brd.py --all
python3 -m unittest discover -s tests -v
python3 scripts/check_sql_exercise.py --step 1
python3 scripts/check_sql_exercise.py --step 2
python3 scripts/check_sql_exercise.py --step 3
python3 scripts/check_sql_exercise.py --all
```

The checks use Python's standard library; no package installation is needed for Modules 1 or 2.

## Ethical and reproducible analysis

- All values in the BRD are proposals or synthetic scenario assumptions unless a source is explicitly cited and verified.
- Do not collect names, contact details, religious affiliation, or other personal/sensitive information for this exercise.
- State data limitations, explainable rules, and uncertainty; never claim that a model proves community demand.
- Keep the project reproducible and describe what evidence would be required before a real decision.

## License

This project is available under the MIT License. See `LICENSE`.
