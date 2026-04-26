# Failed Approaches: What Didn't Work and Why

## 1. Single-Step Synthesis

**What I tried first.** One AI Builder action that took the raw inputs and produced the final report.

**Why it broke.** Two failure modes. First, on weeks with mixed source types (long meeting notes + brief Slack snippets + dense ticket data), the model would over-weight the longest source and miss key items from shorter ones. Second, the output structure was inconsistent across runs, even with detailed prompts.

**What I changed.** Split into three steps: classify → synthesize → render. The classification step gives equal weight to each item regardless of source length. Synthesis operates on the structured items, not raw text. Rendering is purely a formatting concern.

**Lesson.** Multi-step AI pipelines beat one-shot prompts for any task with structured output requirements. The cost is more flow complexity and more AI calls. The benefit is reliability.

---

## 2. Auto-Send to Teams Channel

**What I tried first.** The flow posted directly to a Teams channel as the final step.

**Why it broke.** I caught myself before I shipped this, but in testing it was clear: any AI-generated content that auto-broadcasts is a liability. One bad synthesis (a hallucinated risk, a misattributed decision) and the PM's credibility takes the hit, not the tool's.

**What I changed.** The flow drafts the message and posts it to the PM's draft folder or as a Teams card marked "Draft - PM review needed". The PM is always the human-in-the-loop on broadcast.

**Lesson.** AI in PM workflows should expand human judgment, not replace it. The friction of manual review is the feature, not a bug.

---

## 3. Free-Text Input Concatenation

**What I tried first.** Concatenated all inputs into one giant string and passed to the model.

**Why it broke.** The model couldn't reliably distinguish what came from where. Items got attributed to the wrong source ("according to the meeting notes" when it was actually a Slack message).

**What I changed.** Wrapped each source in explicit markers (`=== MEETING NOTES ===`, etc.) and required the classification step to output the source per item.

**Lesson.** Structured input markers are essentially free and dramatically improve attribution accuracy.

---

## 4. Same Prompt for All Three Audiences

**What I tried first.** A single render prompt that took an `audience` parameter and adjusted output.

**Why it broke.** Worked OK, but the exec output kept leaking technical detail and the all-hands output kept sounding clinical. The single prompt had to be too generic to nail any one audience.

**What I changed.** Same prompt, but with audience-specific guidance sections that the prompt explicitly references. The structure is "if audience == X, follow these rules:" inside the system prompt. Output quality improved noticeably.

**Lesson.** Conditional logic inside a single prompt works better than three separate prompts for cost (one AI call instead of three) and consistency (same model, same context window).

---

## 5. Padding Empty Sections

**What I tried first.** When the synthesis had no decisions needed, the model would invent one to fill the section.

**Why it broke.** Obviously a credibility killer. PMs would catch invented decisions immediately.

**What I changed.** Explicit instruction: "Do NOT pad. If there are no decisions needed, return an empty array, not a fabricated one." Combined with a rendering rule that hides empty sections instead of writing "No decisions needed this week" boilerplate.

**Lesson.** Models default to filling space. They need explicit permission to leave space empty.
