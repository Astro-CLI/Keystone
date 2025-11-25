# Packet Tracer Version Control with Git & GitHub

This guide provides a straightforward workflow for using `git` and the GitHub CLI (`gh`) to save and document changes to your Packet Tracer (`.pkt`) files in a GitHub repository.

## 1. First-Time Setup

You only need to do this once for the project.

### 1.1. Install `git` and `gh`

If you don't have them installed, open a terminal and follow the instructions for your operating system:

- **git:** [Installing Git Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- **gh:** [Installing gh Guide](https://github.com/cli/cli#installation)

### 1.2. Authenticate with GitHub

Connect the `gh` CLI to your GitHub account. It will ask you to log in through your browser.

```bash
gh auth login
```

### 1.3. Initialize a Local Git Repository

If you haven't already, initialize a `git` repository in this project folder.

```bash
git init -b main
```

### 1.4. Create a GitHub Repository and Push Initial Files

This command creates a new **private** repository on your GitHub account, adds your current files, and pushes them.

**IMPORTANT**: Replace `your-repo-name` with a name you choose (e.g., `packet-tracer-project`).

```bash
# Create the repository and link it to your local project
gh repo create your-repo-name --private --source=. --remote=origin

# Add all files to git (including the .pkt files and this README)
git add .

# Make your first commit
git commit -m "Initial commit: Project setup and first Packet Tracer files"

# Push the files to your new GitHub repository
git push -u origin main
```

Your project is now set up and linked to GitHub!

---

## 2. Daily Workflow

Follow these steps every time you make a change to your Packet Tracer files that you want to save.

### Step 1: Make Your Changes

Open your `.pkt` files in Packet Tracer and make your changes as you normally would. Save the file.

### Step 2: Check the Status

Open a terminal in this project directory and run `git status`. It will show you which files have been modified.

```bash
git status
```

### Step 3: Add the Files to a "Commit"

Add the modified files to the next "snapshot" (commit).

```bash
# To add all modified files
git add .

# Or, to add a specific file
# git add YourFileName.pkt
```

### Step 4: Commit Your Changes with a Message

"Committing" saves a snapshot of your changes. The message (`-m`) is crucial—it's your note to your future self explaining *what* you changed.

**Good commit message examples:**
- `git commit -m "feat: Configure OSPF on Core routers"`
- `git commit -m "fix: Corrected VLAN assignment on DMZ switch"`
- `git commit -m "docs: Update network diagram with new IP scheme"`

```bash
git commit -m "Your detailed message about the changes you made"
```

### Step 5: Push Your Changes to GitHub

Send your committed changes to your GitHub repository.

```bash
git push
```

That's it! Your changes are now safely stored on GitHub.

### Quick Workflow Summary

Here are the daily commands in sequence:

```bash
# 1. Check what you've changed
git status

# 2. Add the files
git add .

# 3. Save the changes with a descriptive message
git commit -m "feat: Add and configure the new web server in the DMZ"

# 4. Upload to GitHub
git push
```
