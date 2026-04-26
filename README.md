# \# Cross-Functional Status Synthesizer

# 

# > An AI tool that synthesizes scattered weekly inputs (meeting notes, Teams threads, ticket data, PM notes) into structured executive status reports for cross-functional program management.

# 

# \*\*Status\*\*: v1 prototype, deployed

# \*\*Author\*\*: Sabeela Fatima

# \*\*Stack\*\*: Python, Anthropic Claude API, Streamlit

# \*\*Live Demo\*\*: \[sabeela-status-synthesize.streamlit.app](https://sabeela-status-synthesize.streamlit.app/)

# 

# \---

# 

# \## The Problem This Solves

# 

# Program Managers running cross-functional hardware programs typically draft a weekly status report by reading:

# 

# \- 5-15 meeting notes from working sessions

# \- Teams threads from the prior week

# \- Ticket / JIRA updates from engineering and ops

# \- Email threads with vendors or partners

# \- Their own tracker or RAID log

# 

# The synthesis is the actual job. The typing is filler. Most PMs spend 3-5 hours on this every week, and most of that time is mechanical, not analytical.

# 

# This tool automates the mechanical part. A PM provides their inputs, the tool runs them through a 3-stage AI pipeline, and outputs a structured weekly status report tailored for one of three audiences: executive, engineering leads, or all-hands.

# 

# \## Why AI

# 

# The simple version of "summarize my notes" is a single ChatGPT prompt. That's a toy.

# 

# The non-trivial version handles four behaviors:

# 

# 1\. \*\*Multi-source synthesis\*\*: notes from different meetings about the same workstream get merged, not concatenated.

# 2\. \*\*Workstream classification\*\*: each input gets tagged (Hardware / Firmware / Manufacturing / Vendor / Risk / Decision / Win) so the output groups intelligently.

# 3\. \*\*Audience-specific tone\*\*: same underlying facts, three audience-specific renderings.

# 4\. \*\*Confidence flagging\*\*: items with thin source data get marked "needs verification" rather than padded with confident-sounding filler.

# 

# Those four behaviors are what make this useful instead of decorative.

# 

\## Architecture
┌──────────────────────────────────────────────────────────────┐
===

# │                       INPUT SOURCES                          │

# │   ├── meeting-notes/    (.txt)                               │

# │   ├── teams-channels/   (.txt)                               │

# │   ├── ticket-summary/   (.csv)                               │

# │   └── pm-notes/         (.txt)                               │

# └─────────────────────┬────────────────────────────────────────┘

# │

# ▼

# ┌──────────────────────────────────────────────────────────────┐

# │              PYTHON PIPELINE (synthesize.py)                 │

# │                                                              │

# │  Stage 1: AI classification (workstream, confidence)         │

# │  Stage 2: AI synthesis (structured fields, JSON)             │

# │  Stage 3: AI rendering (audience-specific output)            │

# └─────────────────────┬────────────────────────────────────────┘

# │

# ▼

# ┌──────────────────────────────────────────────────────────────┐

# │                       OUTPUTS                                │

# │  - Markdown status report per audience                       │

# │  - Streamlit UI for interactive demo                         │

# │  - Downloadable .md file from the UI                         │

└──────────────────────────────────────────────────────────────┘

\*\*Key design choice\*\*: human-in-the-loop is preserved. The tool generates a draft, the PM reviews and sends. The system does not auto-send anything. That separation is the difference between a useful tool and a liability.
===

# 

# \*\*AI fallback\*\*: the tool runs in mock mode (deterministic Python logic, no API calls) when no API key is set. This means anyone can clone the repo and run the demo without credentials.

# 

# \## Demo Inputs (Synthetic)

# 

# The `samples/inputs/` folder contains a complete synthetic week of inputs for a fictional hardware NPI program (Project Atlas):

# 

# \- 5 meeting notes (engineering sync, PVT kickoff, vendor sync, manufacturing review, exec checkin)

# \- 1 Teams channel export (15 messages across 3 channels)

# \- 1 ticket summary CSV (12 tickets across statuses)

# \- 1 PM personal notes file

# 

# Run the pipeline against these and you get sample outputs in `samples/outputs/`.

# 

\## Sample Output (Exec Audience)
WEEKLY STATUS — Project Atlas — Week of 2025-10-13
===

# EXECUTIVE SUMMARY

# PVT pilot build kicked off Wednesday with 47 of 50 units to spec on first pass.

# Sensor yield (91% vs. 97% target) is the schedule-critical risk and requires a

# decision on Monday: accept-with-binning or retune placement equipment with

# one-week impact. Vendor MFG-007 quality review escalated to a supplier visit next week.

# KEY RISKS

# 

# Sensor yield 91% vs 97% target; 1-week potential slip if rework path chosen

# Vendor MFG-007: 4 quality escapes in last 60d, on-site review needed

# DisplayWorks Q1 ramp capacity not yet confirmed

# 

# DECISIONS NEEDED

# 

# Sensor yield path: accept-with-binning vs. retune placement

# (Owner: VP Engineering; Deadline: Monday EOD)

# 

# WINS THIS WEEK

# 

# Firmware download issue (DFM-017) root-caused; fix passing 50-unit soak test

# Three P2 DFM issues closed (FPC routing, light pipe, housing color)

# ENC-801 tooling delivery confirmed on schedule

# First-pass PVT yield 94% (target 90%)

# Station 4 throughput up 12% after torque driver recalibration

# 

# LOOKING AHEAD

# 

# Monday: sensor yield decision

# Wednesday: MFG-007 supplier visit

# Thursday: PVT gate review prep begins

# 

# Drafted by AI from PM source inputs. Review before sending.



\## What's in This Repo

status-synthesizer/
===

# ├── README.md

# ├── requirements.txt

# ├── src/

# │   ├── synthesize.py         # 3-stage AI pipeline

# │   └── streamlit\_app.py      # Interactive demo UI

# ├── prompts/

# │   ├── classify\_prompt.md    # Workstream classification prompt

# │   ├── synthesize\_prompt.md  # Structured synthesis prompt

# │   └── render\_prompt.md      # Audience-specific rendering prompt

# ├── samples/

# │   ├── inputs/               # Synthetic weekly inputs

# │   └── outputs/              # Generated outputs (3 audiences)

# ├── flow/

# │   └── flow\_overview.md      # Reference: porting to Power Automate

# └── docs/

└── failed\_approaches.md  # Honest log of design dead ends

## How to Run This Yourself
===

# 

# ```bash

# \# Clone and install

# git clone https://github.com/sabeelafatima/status-synthesizer.git

# cd status-synthesizer

# pip install -r requirements.txt

# 

# \# (Optional) Set Claude API key for full AI mode

# export ANTHROPIC\_API\_KEY="your\_key\_here"

# 

# \# Run the pipeline

# python src/synthesize.py

# 

# \# Run interactive Streamlit demo

# streamlit run src/streamlit\_app.py

# ```

# 

# \## Why Python Instead of Power Automate

# 

# The original design called for Power Automate + AI Builder. I switched to Python because:

# 

# 1\. \*\*Portability\*\*: Python + Claude API runs on any environment. Power Automate ties the workflow to a Microsoft tenant with AI Builder credits.

# 2\. \*\*Defensibility\*\*: a deployed Python demo URL is easier to share than a Power Automate flow screenshot.

# 3\. \*\*Architecture is portable\*\*: the prompts, classification logic, and audience templates ported directly. Anyone with AI Builder credits can recreate this in Power Automate using `flow/flow\_overview.md`.

# 

# The end product is functionally equivalent. The trade-off is Microsoft ecosystem signal vs. shareable demo. For a portfolio prototype, the demo wins.

# 

# \## Honest Limitations

# 

# \- Sample inputs are synthetic; real PM inputs would have more shape and noise.

# \- The pipeline assumes English source content.

# \- Mock mode (deterministic fallback) demonstrates the architecture without AI; full AI mode requires an API key.

# \- Tone calibration is via prompt, not fine-tuning. A production version would build a feedback loop where edited outputs train the next iteration.

# 

# \---

# 

\*\*Built by Sabeela Fatima\*\* | \[GitHub](https://github.com/sabeelafatima) | \[Live Demo](https://sabeela-status-synthesize.streamlit.app/)


===

