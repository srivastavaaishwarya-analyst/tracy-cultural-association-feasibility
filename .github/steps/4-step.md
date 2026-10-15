## Step 4: Review the BRD in a pull request

The BRD is the contract for later analysis. Use a pull request to make the assumptions and trade-offs visible before moving on to data design.

### 📖 Theory: Combine automated and human review

Pull requests create a checkpoint where reviewers can question assumptions and requirements before downstream analysis makes them costly to change. Automated checks catch missing structure and placeholders, but human review is still needed to judge whether decision framing is ethical, understandable, and useful.

### ⌨️ Activity: Request and resolve review

1. Open a pull request that includes `docs/brd.md`. In the description, summarize the decision you framed and identify at least one unresolved assumption or limitation.
2. Read the automated check feedback. If a check fails, update the BRD and push again; do not bypass a check by deleting a requirement or presenting a fabricated fact as real.
3. Request a peer or mentor review if available. Ask whether the objectives and KPIs would support a transparent pilot/no-go/more-data recommendation.

<details>
<summary>Having trouble? 🤷</summary><br/>

- The final check runs against the pull request's BRD while using the trusted validator from the base branch.
- A structural pass means the document meets the exercise criteria; it does not mean stakeholders have approved your assumptions.
- Run `python3 scripts/check_brd.py --all` and `python3 -m unittest discover -s tests -v` before opening the PR.

</details>
