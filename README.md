# Cross-Functional Status Synthesizer

> A Power Automate + AI Builder workflow that synthesizes scattered weekly inputs into structured executive status reports for cross-functional program management.

**Status**: v1 prototype, active build
**Author**: Sabeela [Last Name]
**Stack**: Power Automate, AI Builder (GPT prompt action), Microsoft 365 (OneDrive, Outlook, Teams)

---

## The Problem This Solves

Program Managers running cross-functional hardware or SaaS programs typically draft a weekly status report by reading:

- 5-15 meeting notes from working sessions
- Slack / Teams threads from the prior week
- Ticket / JIRA updates from engineering and ops
- Email threads with vendors or partners
- Their own tracker or RAID log

The synthesis is the actual job. The typing is filler. Most PMs spend 3-5 hours on this every week, and most of that time is mechanical, not analytical.

This workflow automates the mechanical part. A PM drops their inputs into a OneDrive folder (or labels them in Outlook), triggers the flow, and gets back a structured weekly status report formatted for an exec audience, an engineering audience, or an all-hands audience depending on a single parameter.

## Why AI

The simple version of "summarize my notes" is a single ChatGPT prompt. That's a toy.

The non-trivial version handles:

1. **Multi-source synthesis**: notes from different meetings about the same workstream get merged, not concatenated.
2. **Workstream classification**: each input gets tagged (Hardware / Firmware / Manufacturing / Vendor / Risk) so the output groups intelligently.
3. **Tone calibration**: same underlying facts, three audience-specific outputs.
4. **Confidence flagging**: items with thin source data get marked "needs verification" rather than padded with confident-sounding filler.

Those four behaviors are what make this useful instead of decorative.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       INPUT SOURCES                          │
│  OneDrive folder /weekly-status-inputs/                      │
│   ├── meeting-notes/    (.docx, .txt)                        │
│   ├── slack-exports/    (.txt)                               │
│   ├── ticket-summary/   (.csv)                               │
│   └── pm-notes/         (.txt)                               │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│             POWER AUTOMATE FLOW (cloud, scheduled)           │
│                                                              │
│  Step 1: List + read all files in /weekly-status-inputs/     │
│  Step 2: Concatenate with source-type tags                   │
│  Step 3: AI Builder action 1 → workstream classification     │
│  Step 4: AI Builder action 2 → structured synthesis (JSON)   │
│  Step 5: AI Builder action 3 → audience-specific rendering   │
│  Step 6: Compose Word doc + post Teams summary               │
│  Step 7: Move processed inputs to /archive/{week}/           │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│                       OUTPUTS                                │
│  - Word doc in /weekly-status-outputs/{date}-{audience}.docx │
│  - Teams channel post (exec audience version)                │
│  - Email draft to PM lead (with edit prompt)                 │
└──────────────────────────────────────────────────────────────┘
```

**Key design choice**: human-in-the-loop is preserved. The flow drafts and posts as a draft, the PM reviews and sends. The system does not auto-send anything. That separation is the difference between a useful tool and a liability.

## Demo Inputs (Synthetic)

The `samples/` folder contains a complete synthetic week of inputs:

- 5 meeting notes (kickoff, eng standup, vendor sync, manufacturing review, exec checkin)
- 1 Slack export (15 messages across 3 channels)
- 1 ticket summary CSV (12 tickets across statuses)
- 1 PM personal notes file

Run the flow against these inputs and you get the three sample outputs in `samples/outputs/`.

## Sample Output (Exec Audience)

```
WEEKLY STATUS REPORT
Week of 2025-10-13 → 2025-10-19
Program: Project Atlas (Connected Health Wearable)
PM: Sabeela [Last Name]

EXECUTIVE SUMMARY
PVT pilot build kicked off Wednesday with 47/50 units to spec.
Sensor yield issue (DFM-013) is the schedule-critical risk;
mitigation plan reviewed Thursday, decision needed by Monday on
whether to accept or rework. Vendor MFG-007 quality review
escalated; supplier visit scheduled for next week.

KEY RISKS
- Sensor yield 91% vs 97% target; 1-week potential slip if rework path chosen
- Vendor MFG-007: 4 quality escapes in last 60d, on-site review needed
- Display capacity confirmation outstanding for Q1 ramp

DECISIONS NEEDED
- Sensor yield: accept-as-is vs. rework with placement-accuracy fix
  (decision owner: VP Engineering; deadline Monday)

WINS THIS WEEK
- Firmware download issue (DFM-017) root-caused, fix in test
- 3 P2 DFM issues closed
- Procurement confirmed ENC-801 tooling delivery on schedule

LOOKING AHEAD
- Sensor yield decision Monday
- MFG-007 supplier visit Wednesday
- PVT gate review prep begins Thursday
```

## What's in This Repo

```
status-synthesizer/
├── README.md                   # This file
├── flow/
│   ├── flow_overview.md        # Step-by-step flow design
│   └── flow_export.json        # (placeholder) Power Automate flow export
├── prompts/
│   ├── classify_prompt.md      # Workstream classification prompt
│   ├── synthesize_prompt.md    # Structured synthesis prompt
│   └── render_prompt.md        # Audience-specific rendering prompt
├── samples/
│   ├── inputs/                 # Synthetic weekly inputs
│   └── outputs/                # Generated outputs (3 audiences)
└── docs/
    ├── prompt_iteration_log.md # What I tried, what broke, what changed
    └── failed_approaches.md    # Honest log of dead ends
```

## How to Build This Yourself

See `flow/flow_overview.md` for the step-by-step Power Automate setup. Roughly:

1. Set up OneDrive folder structure under your account
2. Create the Power Automate flow with the trigger of your choice (manual button, scheduled, or file-added)
3. Use the prompt templates in `prompts/` as the AI Builder GPT prompt content
4. Configure the output Word doc template
5. Test against the synthetic samples in `samples/inputs/`

Estimated build time: 60-90 minutes if you're familiar with Power Automate.

## Why I Built This

I previously used PPM PRO and Power BI dashboards at a semiconductor company to track NPI status, and the gap between data we collected and the weekly story we told was always the bottleneck. This workflow closes that gap by treating "the weekly story" as a synthesis problem the AI handles, while the data layer stays in the systems of record.

## Honest Limitations

- Sample inputs are synthetic; real meeting notes from real PMs would have different shape and noise.
- The flow assumes English source content. Multilingual workstreams would require additional handling.
- AI Builder GPT prompt action has token limits; very long input weeks need a chunking pre-step.
- Tone calibration is via prompt, not fine-tuning. A real org would build a feedback loop where edited outputs train the next version.

---

**Built by Sabeela [Last Name]** | [LinkedIn](https://linkedin.com/in/...) | [Portfolio](https://...)
