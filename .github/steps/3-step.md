## Step 3: Specify requirements, safeguards, and success metrics

With the decision bounded, specify what a useful decision-support analysis must do and how stakeholders would judge its usefulness. Requirements and KPIs are proposals for validation, not proof that a real organization will succeed.

### 📖 Theory: Connect requirements to decisions

Functional requirements describe what the analysis must do; nonfunctional requirements describe qualities such as privacy, reproducibility, accessibility, and explainability. KPIs connect analysis to stakeholder decisions, but proposed thresholds are not facts until stakeholders validate them. Model accuracy is a technical metric, not a substitute for a business outcome such as budget or capacity fit.

### ⌨️ Activity: Define requirements and KPIs

1. Complete the functional and nonfunctional requirements tables in `docs/brd.md`. Make each requirement testable and explain why it matters.
2. Add at least two decision KPIs. For each, specify a plain-language definition, unit, and the evidence needed to measure it.
3. Commit and push the updated BRD.

<details>
<summary>Having trouble? 🤷</summary><br/>

- A functional requirement might ask for a comparison of program preferences by program type in a synthetic dataset.
- A nonfunctional requirement could state that the analysis must avoid personally identifying data and be reproducible from documented inputs.
- A useful KPI has a unit and a decision connection. Run `python3 scripts/check_brd.py --step 3` for feedback.

</details>
