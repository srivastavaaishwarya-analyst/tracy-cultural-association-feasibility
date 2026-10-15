## Step 1: Open the decision and identify stakeholders

Stakeholders are considering a hypothetical pilot of cultural events, religious celebrations, educational programs, and community gatherings. Before building a dataset or model, establish what decision the analysis should support and who needs to use it.

### 📖 Theory: Start with the decision

A business requirements document starts with the decision someone needs to make, not with a preferred technology. Naming stakeholders and their needs helps an analyst avoid treating one group's preferences as the whole community's demand. This scenario is hypothetical, so the BRD must not present invented community facts as evidence.

### ⌨️ Activity: Create the project context

1. Open the exercise issue created by the `Step 0` workflow and read its scenario and ethics note. If automation did not create an issue, use the **Start Module 1** issue form.
2. Create a working branch, then edit `docs/brd.md`. Write a specific problem statement, name a decision owner or role, and describe at least two stakeholder roles and the decision needs each brings.
3. Commit and push your draft to start the automated check. Keep scenario estimates hypothetical and do not infer local demographics.

<details>
<summary>Having trouble? 🤷</summary><br/>

- A decision owner can be a role, such as a steering group; you do not need to invent a real person's name.
- Stakeholders are people affected by or accountable for the decision. Describe roles, not identities.
- Run `python3 scripts/check_brd.py --step 1` locally to see which context section needs more work.

</details>
