# Showcase walkthrough (~15 min)

**Story:** *"This is a sales analytics platform where every number on the dashboard has been tested, validated and deployed by an automated pipeline, and bad data physically cannot reach it."*

**Screen layout:** the live dashboard, the GitHub **Actions** tab, and your terminal or Claude Code.

---

## 1. Tour of the pipeline (3 min)

1. Open the live dashboard. Point at the **Delivered by CI/CD** panel at the bottom: commit, pipeline run number and data timestamp. Every number is traceable.
2. Click the run number to open the run page and show the **job graph**:
   `Lint & tests (matrix) + Workflow lint` → `Data quality gate` → `Web build` → `All checks` → `Deploy` → `Smoke test`
3. Scroll to the **run summary**: data-quality result, exported KPIs, deployment URL, smoke test.

## 2. A feature through a pull request (4 min)

```bash
git switch -c feature/dashboard-title
# e.g. change the subtitle text in web/src/app/page.tsx
git commit -am "feat: clarify dashboard subtitle"
git push -u origin feature/dashboard-title
gh pr create --fill
```

- The PR shows the checks running.
- When they finish, a bot comment appears with the **preview URL**. Open it and show the `PREVIEW` badge on the page.
- Merge the PR. The pipeline runs on `main`, deploys to **production**, and the smoke test confirms the new commit is live.

## 3. Bad data is blocked ⭐ (4 min)

```bash
git switch -c data/2026-09-26
cp data-pipeline/data/samples/2026-09-26.csv data-pipeline/data/raw/
git add . && git commit -m "data: add sales for 2026-09-26"
git push -u origin data/2026-09-26
gh pr create --fill
```

- **Data quality gate** goes ❌ red. The run page shows annotations with the exact problems and CSV line numbers: a negative price, a $14,900 typo, a duplicate order, a `Nort` region, a missing customer and a zero quantity.
- **Web build, deploy and smoke test are skipped.** Refresh production: unchanged.
- The run summary says **"Deployment blocked — the live dashboard still shows the last good data."**

Fix it by replacing the file with clean data:

```bash
cd data-pipeline && sales-pipeline generate 2026-09-26 && cd ..
git commit -am "data: fix 2026-09-26 sales file" && git push
```

The pipeline goes ✅ green and the preview updates.

## 4. A code bug is caught (2 min)

In `data-pipeline/src/sales_pipeline/transform.py`, change `*` to `+` in the revenue calculation, then push to a branch or PR.
→ `test_revenue_is_quantity_times_price` fails, and nothing is deployed.

## 5. Rollback (2 min)

If a bad-but-passing change reaches production:

```bash
git revert <commit-sha>     # a new commit that undoes it (safe on shared branches)
git push
```

The pipeline redeploys the previous state. For an emergency, Vercel's dashboard also has **Instant Rollback** to any earlier production deployment.

## Closing line

*"Every change is linted, tested, validated and previewed. Production only ever gets code and data that passed every check, and we can prove which commit is live."*
