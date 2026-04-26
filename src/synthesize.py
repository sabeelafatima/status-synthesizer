"""
Cross-Functional Status Synthesizer.

Reads weekly inputs (meeting notes, slack exports, ticket summaries, PM notes)
from a directory structure, runs them through a 3-stage AI pipeline, and
produces audience-specific weekly status reports.

Pipeline:
    1. Classify items by workstream (Hardware, Firmware, Manufacturing, etc.)
    2. Synthesize classified items into structured fields
    3. Render audience-specific output (exec, eng-leads, all-hands)

Falls back to a deterministic mock if no API key is set, so the demo
always works for portfolio review.
"""

import csv
import json
import os
from pathlib import Path
from typing import Optional

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # type: ignore


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "inputs"
OUTPUTS_DIR = Path(__file__).parent.parent / "samples" / "outputs"


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if "## System Prompt" in text:
        parts = text.split("## System Prompt", 1)[1]
        if "##" in parts[5:]:
            parts = parts[: parts.index("##", 5)]
        return parts.strip()
    return text


def gather_inputs(base_dir: Path = None) -> str:
    """
    Read all weekly inputs from the samples directory and concatenate them
    with explicit source markers so the AI can attribute items correctly.
    """
    if base_dir is None:
        base_dir = SAMPLES_DIR

    sections = []
    source_map = {
        "meeting-notes": "MEETING NOTES",
        "slack-exports": "SLACK EXPORTS",
        "ticket-summaries": "TICKET SUMMARIES",
        "pm-notes": "PM NOTES",
    }

    for folder, label in source_map.items():
        folder_path = base_dir / folder
        if not folder_path.exists():
            continue
        sections.append(f"=== {label} ===")
        for file_path in sorted(folder_path.iterdir()):
            if file_path.is_file():
                sections.append(f"\n--- File: {file_path.name} ---")
                sections.append(file_path.read_text(encoding="utf-8"))
        sections.append("")

    return "\n".join(sections)


def call_claude(
    system_prompt: str,
    user_message: str,
    api_key: Optional[str] = None,
    max_tokens: int = 2000,
    model: str = "claude-opus-4-7",
) -> str:
    """Call Claude API with a system prompt and user message."""
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if api_key is None or Anthropic is None:
        return ""

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    text = response.content[0].text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return text


def classify_items(all_inputs: str) -> list[dict]:
    """Stage 1: classify raw inputs into structured items."""
    system = load_prompt("classify_prompt")
    if not system:
        system = (
            "Classify each item in the input into JSON objects with fields: "
            "item, workstream, source, confidence, needs_verification, raw_excerpt. "
            "Return a JSON array."
        )

    response = call_claude(system, all_inputs, max_tokens=4000)
    if not response:
        return _mock_classify(all_inputs)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return _mock_classify(all_inputs)


def synthesize(items: list[dict]) -> dict:
    """Stage 2: synthesize classified items into structured fields."""
    system = load_prompt("synthesize_prompt")
    if not system:
        system = (
            "Synthesize the items into JSON with fields: executive_summary, "
            "key_risks, decisions_needed, wins, looking_ahead. Return JSON only."
        )

    items_json = json.dumps(items, indent=2)
    response = call_claude(system, items_json, max_tokens=2000)
    if not response:
        return _mock_synthesize(items)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return _mock_synthesize(items)


def render(synthesis: dict, audience: str, program_name: str, week_label: str) -> str:
    """Stage 3: render audience-specific report."""
    system = load_prompt("render_prompt")
    if not system:
        system = (
            f"Render the synthesis as a weekly status report for the {audience} "
            "audience. Include header line and closing draft notice."
        )

    payload = {
        "synthesis": synthesis,
        "audience": audience,
        "program_name": program_name,
        "week_label": week_label,
    }
    response = call_claude(system, json.dumps(payload, indent=2), max_tokens=2000)
    if not response:
        return _mock_render(synthesis, audience, program_name, week_label)
    return response


def _mock_classify(all_inputs: str) -> list[dict]:
    """Deterministic fallback that produces realistic items from the synthetic data."""
    return [
        {
            "item": "PVT pilot build kicked off; 47 of 50 units to spec on first pass",
            "workstream": "Manufacturing",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "50 units kitted, 47 built to spec on first pass",
        },
        {
            "item": "Sensor SEN-301 yield at 91% vs 97% target (DFM-013)",
            "workstream": "Risk",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "Sensor yield (DFM-013) at 91%, target 97%",
        },
        {
            "item": "Sensor yield decision needed by Monday EOD; VP Eng owns",
            "workstream": "Decision",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "Need PM + VP Eng decision on sensor yield path by Monday EOD",
        },
        {
            "item": "Supplier MFG-007 (EastBay Magnetics): 4 quality escapes despite PPAP approved",
            "workstream": "Vendor",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "MFG-007 had 4 quality escapes in last 60 days despite PPAP approved",
        },
        {
            "item": "MFG-007 supplier visit scheduled for next week, led by Tomasz",
            "workstream": "Vendor",
            "source": "slack",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "MFG-007 visit being set up for Wednesday",
        },
        {
            "item": "Firmware download issue (DFM-017) root caused; fix passing 50-unit soak test",
            "workstream": "Firmware",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "FW download bug repro confirmed. Boot ROM init timing race. Fix in branch.",
        },
        {
            "item": "Three P2 DFM issues closed: FPC routing, light pipe, housing color",
            "workstream": "Win",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "DFM-007, DFM-019, DFM-016 all closed",
        },
        {
            "item": "ENC-801 tooling delivery confirmed on schedule",
            "workstream": "Schedule",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "ENC-801 tooling delivery confirmed for next Wednesday",
        },
        {
            "item": "DisplayWorks (MFG-011) Q1 ramp capacity confirmation outstanding",
            "workstream": "Vendor",
            "source": "meeting-notes",
            "confidence": "MEDIUM",
            "needs_verification": False,
            "raw_excerpt": "Q1 ramp capacity confirmation: still pending",
        },
        {
            "item": "DFM-014 housing hinge fit closed with one-word resolution; needs verification",
            "workstream": "Risk",
            "source": "meeting-notes",
            "confidence": "MEDIUM",
            "needs_verification": True,
            "raw_excerpt": "DFM-014 marked closed but resolution note in tracker just says 'Closed'",
        },
        {
            "item": "First-pass yield at PVT pilot was 94% (target 90%)",
            "workstream": "Win",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "First-pass yield at PVT pilot was 94%, beat the 90% target",
        },
        {
            "item": "Station 4 throughput up 12% after torque driver recalibration",
            "workstream": "Win",
            "source": "meeting-notes",
            "confidence": "HIGH",
            "needs_verification": False,
            "raw_excerpt": "Test station 4 throughput up 12% after torque driver recalibration",
        },
    ]


def _mock_synthesize(items: list[dict]) -> dict:
    """Deterministic synthesis from classified items."""
    return {
        "executive_summary": (
            "PVT pilot build kicked off Wednesday with 47 of 50 units to spec on first pass. "
            "Sensor yield (91% vs. 97% target) is the schedule-critical risk and requires a "
            "decision on Monday: accept-with-binning or retune placement equipment with "
            "one-week impact. Vendor MFG-007 quality review escalated to a supplier visit next week."
        ),
        "key_risks": [
            {
                "risk": "Sensor yield 91% vs. 97% target on SEN-301 placement",
                "impact": "Potential 1-week schedule slip if rework path chosen",
                "mitigation_status": "Investigation underway; decision Monday",
            },
            {
                "risk": "Vendor MFG-007: 4 quality escapes in last 60 days despite PPAP approved",
                "impact": "Supply confidence risk for ramp",
                "mitigation_status": "Supplier visit scheduled Wednesday",
            },
            {
                "risk": "DisplayWorks Q1 ramp capacity not yet confirmed",
                "impact": "May require qualifying second source if not resolved by mid-November",
                "mitigation_status": "Following up by 2025-10-30",
            },
        ],
        "decisions_needed": [
            {
                "decision": "Sensor yield path: accept-with-binning vs. retune placement",
                "owner": "VP Engineering",
                "deadline": "Monday EOD",
            },
        ],
        "wins": [
            "Firmware download issue root-caused; fix passing 50-unit soak test",
            "Three P2 DFM issues closed (FPC routing, light pipe, housing color)",
            "ENC-801 tooling delivery confirmed on schedule",
            "First-pass yield at PVT pilot: 94% (target 90%)",
            "Station 4 throughput up 12% after torque driver recalibration",
        ],
        "looking_ahead": [
            "Monday: sensor yield decision",
            "Wednesday: MFG-007 supplier visit",
            "Thursday: PVT gate review prep begins",
        ],
    }


def _mock_render(synthesis: dict, audience: str, program_name: str, week_label: str) -> str:
    """Deterministic fallback render for when no API key is available."""
    header = f"WEEKLY STATUS — {program_name} — {week_label}\n"

    if audience == "exec":
        body = [
            header,
            "EXECUTIVE SUMMARY",
            synthesis["executive_summary"],
            "",
            "DECISIONS NEEDED",
        ]
        for d in synthesis["decisions_needed"]:
            body.append(f"- {d['decision']} (Owner: {d['owner']}, Deadline: {d['deadline']})")
        body.extend(["", "KEY RISKS"])
        for r in synthesis["key_risks"]:
            body.append(f"- {r['risk']}. Impact: {r['impact']}")
        body.extend(["", "WINS THIS WEEK"])
        for w in synthesis["wins"]:
            body.append(f"- {w}")
        body.extend(["", "LOOKING AHEAD"])
        for la in synthesis["looking_ahead"]:
            body.append(f"- {la}")
    elif audience == "eng-leads":
        body = [
            header,
            "Audience: Engineering Leads",
            "",
            "KEY RISKS",
        ]
        for r in synthesis["key_risks"]:
            body.append(f"- {r['risk']}")
            body.append(f"  Impact: {r['impact']}")
            body.append(f"  Status: {r['mitigation_status']}")
        body.extend(["", "DECISIONS NEEDED"])
        for d in synthesis["decisions_needed"]:
            body.append(f"- {d['decision']} (Owner: {d['owner']}, Deadline: {d['deadline']})")
        body.extend(["", "LOOKING AHEAD"])
        for la in synthesis["looking_ahead"]:
            body.append(f"- {la}")
        body.extend(["", "WINS"])
        for w in synthesis["wins"]:
            body.append(f"- {w}")
        body.extend(["", "EXECUTIVE SUMMARY", synthesis["executive_summary"]])
    else:  # all-hands
        body = [
            header,
            "Audience: All-Hands",
            "",
            "WINS THIS WEEK",
            "A great week for cross-team execution:",
        ]
        for w in synthesis["wins"]:
            body.append(f"- {w}")
        body.extend(["", "EXECUTIVE SUMMARY", synthesis["executive_summary"]])
        body.extend(["", "LOOKING AHEAD"])
        for la in synthesis["looking_ahead"]:
            body.append(f"- {la}")
        body.extend(["", "AREAS OF FOCUS"])
        for r in synthesis["key_risks"][:2]:
            body.append(f"- {r['risk']}")

    body.extend(["", "Drafted by AI from PM source inputs. Review before sending."])
    return "\n".join(body)


def run_pipeline(
    program_name: str = "Project Atlas",
    week_label: str = "Week of 2025-10-13",
    audiences: list[str] = None,
) -> dict:
    """Run the full pipeline and return classified items, synthesis, and rendered outputs."""
    if audiences is None:
        audiences = ["exec", "eng-leads", "all-hands"]

    all_inputs = gather_inputs()
    items = classify_items(all_inputs)
    synthesis = synthesize(items)

    rendered = {}
    for audience in audiences:
        rendered[audience] = render(synthesis, audience, program_name, week_label)

    return {
        "items": items,
        "synthesis": synthesis,
        "rendered": rendered,
    }


if __name__ == "__main__":
    result = run_pipeline()

    print(f"Classified {len(result['items'])} items")
    print(f"Synthesis fields: {list(result['synthesis'].keys())}")
    print()

    # Save outputs to disk
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    for audience, text in result["rendered"].items():
        output_path = OUTPUTS_DIR / f"latest_{audience}.md"
        output_path.write_text(text, encoding="utf-8")
        print(f"Wrote {output_path}")

    print("\n--- EXEC OUTPUT PREVIEW ---")
    print(result["rendered"]["exec"][:800])