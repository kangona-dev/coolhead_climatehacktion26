# Working together with Git (beginner guide)

Git keeps one shared copy of the code on GitHub. Everyone downloads it, makes changes on their
own laptop, and sends them back. The easiest way, with no typing commands, is **GitHub Desktop**.

---

## ONE-TIME SETUP

### Step 1 – Everyone: make accounts and install
1. Make a free account at **github.com**.
2. Install **GitHub Desktop** from **desktop.github.com** and sign in with your GitHub account.

### Step 2 – ONE person (Kangona): put the project on GitHub
1. Unzip `coolhead.zip`. It already has git set up and a first save ("commit") inside.
2. In GitHub Desktop: **File → Add local repository** → choose the `coolhead` folder → **Add repository**.
3. Click **Publish repository** (top bar).
   - Name: `coolhead`
   - **Untick "Keep this code private"** if you want judges to see it (they usually need to).
   - Click **Publish repository**.
4. On github.com, open the repo → **Settings → Collaborators → Add people** → add each teammate's
   GitHub username. They'll get an email invite to accept.

### Step 3 – Teammates: download the shared copy
1. Accept the invite email.
2. In GitHub Desktop: **File → Clone repository** → pick `coolhead` → choose where to save → **Clone**.
3. Click **Open in Visual Studio Code**, then do README Part A, steps 4–5 (install libraries, run the tests).

---

## THE DAILY LOOP (every time you work)

```
1. FETCH / PULL   → get everyone else's latest changes
2. EDIT           → change code in VS Code
3. TEST           → python tests/test_model.py
4. COMMIT         → save a snapshot with a short message
5. PUSH           → send it to GitHub
```

In GitHub Desktop:
1. **Before you start:** click **Fetch origin**. If it changes to **Pull origin**, click it.
2. Make your changes in VS Code and save the files.
3. Run the tests.
4. Back in GitHub Desktop, your changed files are listed on the left. At the bottom left, write a
   short summary, like `Add real NSW tariff`, then click **Commit to main**.
5. Click **Push origin**.

**Commit and push small and often**, every 30–60 minutes. Big, rare pushes cause clashes.

---

## TEAM RULES (avoid clashes)

Each person mostly edits their **own files**:

| Person | Owns |
|---|---|
| Data & model | `coolhead/model.py` (room presets, fixes), `backtest.py` |
| Planner & prices | `coolhead/data.py`, the tariff in `coolhead/model.py` (tell the model person first) |
| App | `app.py` |
| Kangona (story) | `README.md`, `DISCLOSURES.md`, pitch files in a `pitch/` folder |

- Need to change someone else's file? **Message them first** in the team chat.
- **Never push code that fails the tests.** If the online app breaks, the demo breaks.
- Don't commit passwords or API keys. (`.gitignore` already blocks the usual places.)

---

## "IT SAYS CONFLICT" – don't panic

A conflict means two people changed the same lines. GitHub Desktop will show the file.
1. Open it in VS Code. You'll see blocks marked `<<<<<<<`, `=======` and `>>>>>>>`.
2. VS Code shows buttons above each block: **Accept Current**, **Accept Incoming** or **Accept Both**.
   Pick the right one (ask the other person if unsure).
3. Make sure no `<<<<<<<` lines remain, save, run the tests, then **Commit merge** and **Push origin**.

Can't fix it? Paste the file into Claude or ask a mentor. Don't delete the folder and start over.

---

## PUT THE APP ONLINE (connects to the shared repo)

1. Go to **share.streamlit.io** and sign in with GitHub (only one person needs to do this).
2. **Create app** → choose the `coolhead` repo, branch `main`, file `app.py` → **Deploy**.
3. You get a public link. **Every push to `main` updates the live app automatically**,
   which is why the "never push broken code" rule matters.

**Data for the offline demo:** after running `python backtest.py` once with internet, the `data/`
folder has saved copies of the weather and prices. Commit and push those files too, so the online
app still works if a data website goes down during judging.

---

## Prefer typing commands? (optional)

```
git pull                        # get latest
git add .                       # stage your changes
git commit -m "What I changed"  # save a snapshot
git push                        # send to GitHub
git status                      # what's changed?
git log --oneline               # history
```
