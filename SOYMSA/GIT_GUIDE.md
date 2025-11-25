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