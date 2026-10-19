---
description: Create a new milestone with phases
argument-hint: "<milestone-name>"
---

# /new-milestone Workflow

<objective>
Define a new milestone with goal, phases, and success criteria.
</objective>

<process>

## 1. Validate SPEC Exists

**PowerShell:**
```powershell
if (-not (Test-Path ".gsd/SPEC.md")) {
    Write-Error "SPEC.md required. Run /new-project first."
}
```

**Bash:**
```bash
if [ ! -f ".gsd/SPEC.md" ]; then
    echo "Error: SPEC.md required. Run /new-project first." >&2
fi
```

---

## 2. Gather Milestone Information

Ask for:
- **Name** — Milestone identifier (e.g., "v1.0", "MVP", "Beta")
- **Goal** — What does this milestone achieve?
- **Must-haves** — Non-negotiable deliverables
- **Nice-to-haves** — Optional if time permits

---

## 3. Generate Phase Breakdown

Based on goal and must-haves, suggest phases:

```markdown
## Suggested Phases

Phase 1: {Foundation/Setup}
Phase 2: {Core Feature A}
Phase 3: {Core Feature B}
Phase 4: {Integration/Polish}
Phase 5: {Verification/Launch}
```

Ask user to confirm or modify.

---

## 4. Update ROADMAP.md

```markdown
# ROADMAP.md

> **Current Milestone**: {name}
> **Goal**: {goal}

## Must-Haves
- [ ] {must-have 1}
- [ ] {must-have 2}

## Phases

### Phase 1: {name}
**Status**: ⬜ Not Started
**Objective**: {description}

### Phase 2: {name}
**Status**: ⬜ Not Started
**Objective**: {description}

...
```

---

## 5. Update STATE.md

```markdown
## Current Position
- **Milestone**: {name}
- **Phase**: Not started
- **Status**: Milestone planned
```

---

## 5b. Reset Session Files (if starting fresh)

If DECISIONS.md or JOURNAL.md contain entries from a previous milestone, reset them to prevent monolithic growth:

**PowerShell:**
```powershell
# Archive decisions and journal if files contain entries from previous work
$archiveDir = ".gsd/milestones/pre-$name"
if (Test-Path -LiteralPath $archiveDir) {
    Write-Error "Backup destination already exists: $archiveDir"
    exit 1
}
if ((Test-Path ".gsd/DECISIONS.md") -and (Get-Content ".gsd/DECISIONS.md" | Measure-Object -Line).Lines -gt 5) {
    New-Item -ItemType Directory -Path $archiveDir | Out-Null
    Copy-Item ".gsd/DECISIONS.md" "$archiveDir/DECISIONS.md"
    Set-Content ".gsd/DECISIONS.md" "# Decisions`n`n> Previous decisions archived in $archiveDir/DECISIONS.md`n`n---`n"
}
if ((Test-Path ".gsd/JOURNAL.md") -and (Get-Content ".gsd/JOURNAL.md" | Measure-Object -Line).Lines -gt 5) {
    New-Item -ItemType Directory -Path $archiveDir | Out-Null
    Copy-Item ".gsd/JOURNAL.md" "$archiveDir/JOURNAL.md"
    Set-Content ".gsd/JOURNAL.md" "# Journal`n`n> Previous journal entries archived in $archiveDir/JOURNAL.md`n`n---`n"
}
```

**Bash:**
```bash
archive_dir=".gsd/milestones/pre-$name"
if [ -e "$archive_dir" ]; then
    echo "Error: backup destination already exists: $archive_dir" >&2
    exit 1
fi
if [ -f ".gsd/DECISIONS.md" ] && [ "$(wc -l < .gsd/DECISIONS.md)" -gt 5 ]; then
    mkdir "$archive_dir"
    cp ".gsd/DECISIONS.md" "$archive_dir/DECISIONS.md"
    printf "# Decisions\n\n> Previous decisions archived in %s/DECISIONS.md\n\n---\n" "$archive_dir" > .gsd/DECISIONS.md
fi
if [ -f ".gsd/JOURNAL.md" ] && [ "$(wc -l < .gsd/JOURNAL.md)" -gt 5 ]; then
    mkdir -p "$archive_dir"
    cp ".gsd/JOURNAL.md" "$archive_dir/JOURNAL.md"
    printf "# Journal\n\n> Previous journal entries archived in %s/JOURNAL.md\n\n---\n" "$archive_dir" > .gsd/JOURNAL.md
fi
```

> **Note:** Existing entries are automatically backed up to `.gsd/milestones/pre-{name}/` before reset so no prior discussions or decisions are lost. If `/complete-milestone` was run first, files are already archived in the completed milestone directory.

---

## 6. Commit

```bash
git add .gsd/ROADMAP.md .gsd/STATE.md
git commit -m "docs: create milestone {name}"
```

---

## 7. Offer Next Steps

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► MILESTONE CREATED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Milestone: {name}
Phases: {N}

───────────────────────────────────────────────────────

▶ NEXT

/plan 1 — Create Phase 1 execution plans

───────────────────────────────────────────────────────
```

</process>
