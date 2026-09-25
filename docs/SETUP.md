# One-time setup: GitHub + Vercel

This takes about 15 minutes. At the end, every push is tested and deployed automatically.

## 1. Push the code to GitHub

Create an **empty** repository on GitHub (no README or .gitignore), then run:

```bash
cd sales-pulse-platform
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

The first pipeline run starts immediately. Stages 1–3 go green. The deploy stage fails at this point because the Vercel secrets don't exist yet; that's expected.

In `README.md`, replace `OWNER/REPO` in the two badge URLs with `<your-username>/<repo-name>`.

## 2. Create the Vercel project

1. Sign in at [vercel.com](https://vercel.com) (you can use your GitHub account).
2. **Get a token:** Account Settings → **Tokens** → Create. Name it `github-actions` and copy the value.
3. **Create and link the project** from your machine:
   ```bash
   cd web
   npx vercel link          # choose "create new project", name it e.g. sales-pulse
   ```
   When asked *"In which directory is your code located?"*, answer `./`. You are already inside `web/`, and that is where the pipeline runs Vercel from.
4. Open the generated `web/.vercel/project.json` and copy `orgId` and `projectId`. The folder is git-ignored, so it won't be committed.

   *Alternative without the CLI:* the Project ID is under Project → Settings → General, and the Org/Team ID under Team Settings → General.

5. In the Vercel project settings, check that **Root Directory is empty** (not `web`), because the pipeline already runs from inside `web/`.

Git auto-deploys are turned off in `web/vercel.json` (`"git": { "deploymentEnabled": false }`), so **GitHub Actions is the only thing that deploys**. Every deployment has passed the pipeline first.

## 3. Add the secrets to GitHub

In the repo, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret | Value |
|---|---|
| `VERCEL_TOKEN` | the token from step 2.2 |
| `VERCEL_ORG_ID` | `orgId` from `project.json` |
| `VERCEL_PROJECT_ID` | `projectId` from `project.json` |

Or, with the GitHub CLI (it prompts for each value, which keeps it out of your shell history):

```bash
gh secret set VERCEL_TOKEN
gh secret set VERCEL_ORG_ID
gh secret set VERCEL_PROJECT_ID
```

Then re-run the pipeline: **Actions → CI/CD Pipeline → Run workflow**. The production deploy should now succeed.

## 4. Enable the smoke test

Once production is deployed, copy your production URL (e.g. `https://sales-pulse.vercel.app`) and add it as a repository **variable** (not a secret): **Settings → Secrets and variables → Actions → Variables → New variable**, name `PRODUCTION_URL`.

From then on, stage 5 checks that the live site serves each new commit, and the URL appears on the repo's **Deployments** panel.

## 5. Recommended: protect `main`

**Settings → Branches → Add branch ruleset** (or classic branch protection) for `main`:
- ✅ Require a pull request before merging
- ✅ Require status checks to pass, and select **✅ All checks passed**

Now nothing reaches `main`, and so nothing reaches production, without a green pipeline.

> ⚠ If you enable this, the daily data-refresh bot can no longer push to `main` directly. Either add `github-actions[bot]` to the ruleset's bypass list, or change the workflow to open a PR instead.

## 6. Optional: a manual approval gate for production

**Settings → Environments → production → Required reviewers**, then add yourself. Production deploys then pause until someone clicks **Approve** on the run page, which makes a nice moment in a live demo.

## 7. Optional: public preview URLs

Vercel protects preview deployments with Vercel login by default. To let anyone open PR previews (for example, an audience), go to Vercel → Project → Settings → **Deployment Protection** and turn off Vercel Authentication for previews.
