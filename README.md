# AIRS Autonomous Hexacopter Project

Hey everyone, welcome to the central repository for our AIRS Autonomous Hexacopter build. We'll be using this repo to track all our code, scripts, configurations, and documentation over the next 8 weeks. 

As a quick recap, our goal is to build a hexacopter that can autonomously survey a field, use an onboard camera and AI model to detect diseased plants in real-time, and trigger a targeted payload release.

---

## Repository Structure

To keep things organized and prevent us from stepping on each other's toes with merge conflicts, please put your files in the right folders. Let's avoid dumping loose files in the root directory.

*   **/aerospace** 
    *   **Contents:** CAD files, payload mechanism designs, weight/balance spreadsheets, and thrust test data.
*   **/electronics**
    *   **Contents:** Wiring diagrams, power budget calculations, payload actuator circuit designs, and pinout references.
*   **/navigation (Part A)**
    *   **Contents:** Python scripts, SITL configuration files, ArduPilot parameter backups, and mission logic.
*   **/ai_vision (Part B)**
    *   **Contents:** Jupyter Notebooks (for Colab training), dataset download scripts, model export/quantization scripts for the Hailo-8L, and the Raspberry Pi inference pipeline.
*   **/swarm_sim (Part C)**
    *   **Contents:** `pyswarms` simulation logic, fitness functions, and visualization scripts for our multi-drone PSO stretch goal.
*   **/docs**
    *   **Contents:** Team handoff documents, weekly async update logs, and meeting notes (seperate folder to be maintained for each type).

---

## Git Guidelines

To keep our project history readable and make sure we don't accidentally overwrite anyone's hard work, let's stick to a few basic rules:

### 1. Branching
Please don't push directly to the `main` branch. Whenever you start working on something, spin up a new branch.
*   **Format:** `type/your-feature-name`
*   **Examples:**
    *   `feature/new-feature`
    *   `docs/docs`
    *   `fix/fixing-existing-wrong-things`
    *   `refactor/changing-existing-right-things`

### 2. Commit Messages
We're using a standard format for commits so we can easily tell what changed. Just start your message with one of these tags:
*   `feat:` (New feature, script, or design)
*   `fix:` (Bug fix or correcting an error)
*   `docs:` (Changes to documentation or the README)
*   `test:` (Adding or updating tests)
*   `chore:` (Routine tasks, dependency updates)
*   `refactor:` (Rafactoring code)
Note: no need to categories commits for every small fix, only for major changes

> **Example:** `feat: add initial MAVSDK arm and takeoff script`

---

## Dependencies and Suggestions (Very Important):

If you add something to the project, which is dependent on the installation/requirement of something else, then please mention them here (keep points short):

### Current Dependencies/Suggestions:
1. Simulation codes are being run using WSL, so try to use that itself to avoid issues (talk to Aditya if needing help on installing and/or using WSL).

---

## Quick Start Guide

If you're relatively new to Git, just follow this workflow every time you sit down to work:

**Step 1: Get the latest updates**
Always pull the latest changes before starting so you're up to date.
```bash
git checkout main
git pull origin main
```

**Step 2: Create your branch**
```bash
git checkout -b feature/your-task-name
```

**Step 3: Do your work & save it**
Add your files to the correct folder from the structure above.
```bash
git add .
git commit -m "feat: brief description of what you did"
```

**Step 4: Push to the repo**
```bash
git push origin feature/your-task-name
```

**Step 5: Create a Pull Request (PR)**
Head over to the repo online and open a pull request. Tag a teammate to give it a quick review before it gets merged into `main`.

---
