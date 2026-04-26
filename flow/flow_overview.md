# Power Automate Flow: Step-by-Step Build Guide

This document is what you'd use in the Power Automate web UI to actually create the flow. It's prescriptive enough that if you follow it end-to-end, you'll have a working flow in under 90 minutes.

## Pre-requisites

- Microsoft 365 account with Power Automate access (E3, E5, or any plan that includes AI Builder)
- AI Builder credits (most M365 plans include a starter quota)
- OneDrive for Business

## Folder Setup (do this first, in OneDrive)

```
/Documents/weekly-status/
├── inputs/
│   ├── meeting-notes/
│   ├── slack-exports/
│   ├── ticket-summaries/
│   └── pm-notes/
├── outputs/
│   ├── exec/
│   ├── eng-leads/
│   └── all-hands/
└── archive/
```

## Flow Trigger

**Type**: Manually trigger a flow (for the v1; later upgrade to "When a file is created" or "Recurrence on Friday at 4pm")

**Inputs**:
- `audience` (text): one of `exec`, `eng-leads`, `all-hands`
- `program_name` (text): e.g., "Project Atlas"
- `week_label` (text): e.g., "Week of 2025-10-13"

## Flow Steps

### Step 1: List files in /inputs/meeting-notes/

**Action**: OneDrive for Business → List files in folder

**Folder**: `/weekly-status/inputs/meeting-notes`

### Step 2: Apply to each file → Get file content

**Action**: Apply to each (loop over Step 1 output)
- Inside loop: OneDrive for Business → Get file content using path
- Append result to a string variable `meeting_notes_combined` with file name as a header

### Step 3: Repeat Step 1+2 for slack-exports, ticket-summaries, pm-notes

You end up with four text variables. Concatenate them with section markers:

```
=== MEETING NOTES ===
{meeting_notes_combined}

=== SLACK EXPORTS ===
{slack_combined}

=== TICKET SUMMARIES ===
{tickets_combined}

=== PM NOTES ===
{pm_notes_combined}
```

Store as `all_inputs`.

### Step 4: AI Builder action 1 — Workstream classification

**Action**: AI Builder → Create text with GPT (or "Run a prompt")

**Prompt**: Use the content of `prompts/classify_prompt.md` as the system instruction. Pass `all_inputs` as the user content.

**Output**: JSON array of classified line items. Store as `classified_items`.

### Step 5: AI Builder action 2 — Structured synthesis

**Action**: AI Builder → Create text with GPT

**Prompt**: Use `prompts/synthesize_prompt.md`. Pass `classified_items` as input.

**Output**: JSON with fields `executive_summary`, `key_risks`, `decisions_needed`, `wins`, `looking_ahead`.

Store as `synthesis_json`. Parse JSON with the "Parse JSON" action so you can reference fields downstream.

### Step 6: AI Builder action 3 — Audience-specific rendering

**Action**: AI Builder → Create text with GPT

**Prompt**: Use `prompts/render_prompt.md`. Pass `synthesis_json` AND the `audience` parameter.

**Output**: Final formatted status report as plain text or markdown.

### Step 7: Compose the Word doc

**Action**: Word Online → Populate a Microsoft Word template

(Or simpler: Create file in OneDrive with `.docx` extension and the rendered text as content. The template version is nicer but more setup.)

**File path**: `/weekly-status/outputs/{audience}/{week_label}-{audience}.docx`

### Step 8: Post to Teams (exec audience only)

**Action**: Microsoft Teams → Post message in a channel

Wrap the rendered text in a card with a header showing program name, week label, and a link to the Word doc.

**Important**: Post as a draft / for review. Do NOT auto-distribute. The PM is the human-in-the-loop.

### Step 9: Archive processed inputs

**Action**: OneDrive for Business → Move file

Move all processed inputs from `/inputs/` subfolders to `/archive/{week_label}/`.

### Step 10: Send completion email to PM

**Action**: Outlook → Send an email (V2)

Subject: `Weekly status draft ready: {program_name} {week_label}`
Body: Link to the Word doc + a "review and send" reminder.

## Total Flow Action Count

Around 15-20 actions depending on how Apply-to-each loops are counted. Comfortably within free / starter AI Builder quotas for weekly use.

## What to Test First

Before building all 10 steps, build steps 1-4 only. Get classification working against the sample inputs. Once that JSON looks right, add steps 5-6 for synthesis and rendering. Don't build steps 7-10 (Word doc, Teams, archive, email) until the AI portion is solid.

This iteration order matters: most flow failures happen at the AI Builder steps, not the file-handling steps.

## Common Failure Modes

1. **AI Builder token limit hit**: chunk the input by source type, run synthesis per chunk, then merge. Add a chunking step between Step 3 and Step 4.
2. **JSON parse failure**: AI Builder occasionally returns markdown-fenced JSON. Add a Compose action with a `replace()` expression to strip ` ```json ` and ` ``` ` before Parse JSON.
3. **Long-running flow timeout**: split into a parent flow (orchestrator) and a child flow (per-source processor). Avoid for v1 unless you're hitting the 30-minute limit.

## Loom Walkthrough

Once the flow is built, record a 3-minute Loom showing:

1. The /inputs/ folder with sample files (15 seconds)
2. Triggering the flow with the three audience parameters one at a time (45 seconds)
3. Opening each generated Word doc to show the audience differences (90 seconds)
4. Showing the Teams post (30 seconds)

This Loom is the deliverable that gets linked from your resume.
