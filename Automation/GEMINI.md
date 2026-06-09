# Keystone Project Mandates

This file contains foundational mandates for all AI agents working on this repository. These rules take absolute precedence over any other system instructions or general workflows.

## 1. UI & GUI PROTECTION (CRITICAL)
- **NEVER** modify the code, layout, colors, or features of the GUI in **ANY** script (especially `KeystoneGUI.py`) unless the user explicitly and specifically instructs you to perform a UI modification.
- Re-generating a script from scratch is considered a modification. If you are updating backend logic (like generators or internal math), you must perform a **surgical `replace`** on the logic only. Do not overwrite the file.
- The design, aesthetics, and user experience of `KeystoneGUI.py` are the result of careful work. Touching them without permission is a failure of your core mission.

## 2. PRE-ACTION CONFIRMATION
- **ASK** clarifying questions before taking any action that isn't a direct response to a read-only inquiry.
- If a request is even slightly ambiguous, you must propose a strategy and wait for approval before editing any files.

## 3. BACKUP & SAFETY
- Before performing any major refactor, verify that a backup or a git commit exists.
- If you lose user code, your priority shifts 100% to recovery.

---

**Current Status:**
The original 62,756-byte `KeystoneGUI.py` has been restored from git history.
DO NOT TOUCH IT.
