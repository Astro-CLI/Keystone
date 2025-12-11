# Git Workflow for the SOYMSA Project

This is my personal guide for using Git and GitHub to manage this Packet Tracer project. It's a simple but solid workflow to keep track of changes, document progress, and make sure nothing gets lost. Think of it as version control for our own little networking universe.

---

## 1. First-Time Setup

You only need to do this once. Get it done, and you're set.

### 1.1. Install the Tools

If you don't have `git` and `gh` installed, pop open a terminal. You're on Arch, so you know what to do.

```bash
# For Arch Linux
sudo pacman -S git github-cli
```

For other distros or OSes, check the official docs.

### 1.2. Login to GitHub

Next, authenticate the GitHub CLI with your account. It'll open a browser window for you to log in.

```bash
gh auth login
```

### 1.3. Initialize the Local Repo

If you haven't already, initialize a Git repository in this project folder.

```bash
git init -b main
```

### 1.4. Create the GitHub Repo & Push

This command does a few things: it creates a new **private** repository on your GitHub, links your local project to it, and pushes your initial files.

**Heads up**: Replace `your-repo-name` with what you want to call it on GitHub.

```bash
# Create the repo on GitHub and set it as your 'origin' remote
gh repo create your-repo-name --private --source=. --remote=origin

# Stage all current files for the first commit
git add .

# Make your first commit. A good message is a good habit.
git commit -m "Initial commit: Project setup and first .pkt files"

# Push your local files to the new repo on GitHub
git push -u origin main
```

Boom. Your project is live on GitHub.

---

## 2. The Daily Grind

This is the loop you'll follow every time you save meaningful progress on your `.pkt` files.

### Step 1: Do the Work

Open up Packet Tracer, build your network, break things, fix them. Save the file when you hit a good stopping point.

### Step 2: Check Your Changes

Back in the terminal, run `git status`. This is your "mission briefing." It tells you what files you've modified since your last commit. It's a good habit to run this before you do anything else.

```bash
git status
```

### Step 3: Stage Your Files

Add the files you want to include in your next "snapshot" (commit).

```bash
# Add all modified files. Quick and easy.
git add .

# Or, if you want to be specific (sometimes you do)
# git add TheSpecificFileYouChanged.pkt
```

### Step 4: Commit with a Clear Message

A commit saves your staged changes. The message (`-m`) is everything. It's a log for your future self (and for me, if I'm grading this). Make it count. Don't just say "updated files." Explain *what* you did.

Think like a pentester documenting their findings. Be clear, be concise.

**Good commit messages look like this:**
- `git commit -m "feat: Configure OSPF between Core and Distribution layers"`
- `git commit -m "fix: Corrected IP address on the web server in the DMZ"`
- `git commit -m "docs: Update network diagram to reflect new VLANs"`

```bash
git commit -m "Your detailed message about what you accomplished"
```

### Step 5: Push to GitHub

Send your committed changes up to the cloud. This backs up your work and updates the project history.

```bash
git push
```

That's the whole workflow. Your progress is saved and documented.

---

## 3. Keeping Secrets Out of Your Code

This is critically important. Never, ever commit sensitive information to your repository. This includes:

-   Private SSH keys (`id_rsa`, `id_ed25519`)
-   API keys
-   Passwords
-   Configuration files with credentials

Once something is committed to Git, it can be very difficult to remove it completely from the history. Even if you delete the file in a later commit, the original commit still exists in the repository's history.

### Best Practices

1.  **Store Keys Properly**: SSH keys belong in your `~/.ssh/` directory, not in your project folder. This is the default and most secure location.

2.  **Use `.gitignore`**: If for some reason you must have a sensitive file in your project directory, add its name to the `.gitignore` file *before* you ever commit it. This tells Git to ignore the file and never track it.

    For example, to ignore all files starting with `id_ed25519`, you would add this line to your `.gitignore` file:

    ```
    id_ed25519*
    ```

3.  **Check Before You Commit**: Always run `git status` before you run `git add .`. Make sure you are not about to stage sensitive files.

### What If I Mess Up?

If you suspect you might have committed a key, you can search your repository's history. This command searches the entire history of your repository for the phrase "PRIVATE KEY":

```bash
git rev-list --all | xargs -n1 git grep -i "PRIVATE KEY"
```

If this command returns any results, you have a problem. The best solution is to consider that key compromised, generate a new one, and update any systems that used the old key.

---

## 4. Repository Structure

To keep the project organized, files are stored in specific directories. Here's a quick rundown of what you'll find where:

-   **`/` (Root Directory)**
    -   `README.md`: The main entry point for understanding the project.
    -   `LICENSE`: The Apache 2.0 license file.
    -   `.gitignore`: Standard file for ignoring files that shouldn't be in the repo.

-   **`Documentation/`**
    -   This is where all written documentation, diagrams, and supplementary materials go. It's broken down into subdirectories that mirror the network's structure (Core, Distribution, Access).

-   **`Resources/`**
    -   A place for any external resources, templates, or other assets that are useful for the project but aren't part of the core network or documentation.

-   **`SOYMSA/`**
    -   The heart of the project. This directory contains the Packet Tracer (`.pkt`) files that represent the different stages of the network build.
    -   `GIT_GUIDE.md`: The file you're reading right now.

---

## The TL;DR Workflow

When you're in the zone, here are the commands back-to-back:

```bash
# 1. See what you changed
git status

# 2. Stage it all
git add .

# 3. Commit with a purpose
git commit -m "feat: Added a new firewall and configured ACLs"

# 4. Ship it
git push
```
