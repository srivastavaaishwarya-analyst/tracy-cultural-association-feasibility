## Step 2: Bound objectives, scope, and assumptions

Now turn the broad question into a manageable feasibility analysis. Your scope should support a decision without promising to establish an organization or make unsupported claims about an entire community.

### 📖 Theory: Make scope explicit

Objectives should describe observable outcomes that support a decision, while scope and non-goals keep a feasibility study from quietly becoming an unsupported census or an operational promise. Explicit assumptions make scenario calculations reproducible and easy to replace when verified evidence becomes available.

### ⌨️ Activity: Define the boundaries

1. In `docs/brd.md`, add at least two measurable objectives, explain what the analysis includes, and name what it deliberately excludes.
2. Add at least two scenario assumptions. Mark each as hypothetical and describe how it could be checked before a real decision.
3. Commit and push the updated BRD. The next lesson starts only after this step's check passes.

<details>
<summary>Having trouble? 🤷</summary><br/>

- A measurable objective can state a comparison the analysis will make, such as whether a proposed pilot fits a hypothetical budget and capacity limit.
- Do not make up local household counts, religious affiliation, venue availability, or actual prices. Use placeholder assumptions labeled hypothetical.
- Run `python3 scripts/check_brd.py --step 2` for section-specific feedback.

</details>
