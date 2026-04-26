"""
Streamlit Demo App for Status Synthesizer.

Run with:
    streamlit run src/streamlit_app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent))

from synthesize import run_pipeline  # noqa: E402


def main() -> None:
    st.set_page_config(
        page_title="Status Synthesizer",
        page_icon="📋",
        layout="wide",
    )

    st.title("📋 AI-Augmented Status Synthesizer")
    st.caption(
        "Synthesizes meeting notes, Slack threads, ticket data, and PM notes "
        "into structured weekly executive status reports. All sample data is synthetic."
    )

    with st.sidebar:
        st.header("Configuration")
        program_name = st.text_input("Program Name", value="Project Atlas")
        week_label = st.text_input("Week Label", value="Week of 2025-10-13")
        audience = st.selectbox(
            "Audience",
            ["exec", "eng-leads", "all-hands"],
            help="Same underlying synthesis, different framing per audience.",
        )
        st.markdown("---")
        st.markdown("**Inputs Used**")
        st.markdown("- 5 meeting notes")
        st.markdown("- 1 Slack channel export")
        st.markdown("- 1 ticket summary CSV")
        st.markdown("- 1 PM notes file")
        st.markdown("---")
        st.caption(
            "Uses Claude API if `ANTHROPIC_API_KEY` is set, otherwise falls "
            "back to a deterministic mock pipeline so the demo always works."
        )
        run_button = st.button("Generate Status Report", type="primary")

    if not run_button:
        st.info(
            "Configure your program details in the sidebar, then click "
            "'Generate Status Report' to see the AI pipeline in action."
        )

        st.markdown("### How this works")
        st.markdown(
            """
The pipeline runs three AI stages:

**Stage 1 - Classify**: Each item in the raw inputs gets tagged with a workstream
(Hardware, Firmware, Manufacturing, Vendor, Test, Schedule, Risk, Decision, Win),
a confidence level, and a verification flag for ambiguous items.

**Stage 2 - Synthesize**: Classified items get rolled up into structured fields:
executive summary, key risks, decisions needed, wins, and looking ahead. Items
flagged for verification get filtered or labeled.

**Stage 3 - Render**: Same synthesis gets rendered three ways for different
audiences. Exec is direct and business-impact framed. Eng-leads is technical
and peer-to-peer. All-hands is warm and emphasizes team contributions.

**Important design choice**: the AI does NOT auto-send any output. The PM is
always the human-in-the-loop on broadcast.
            """
        )
        return

    with st.spinner("Reading inputs and running AI pipeline..."):
        result = run_pipeline(
            program_name=program_name,
            week_label=week_label,
            audiences=[audience],
        )

    st.markdown("## Generated Status Report")
    st.code(result["rendered"][audience], language="markdown")

    st.download_button(
        label=f"Download {audience}.md",
        data=result["rendered"][audience],
        file_name=f"{week_label.replace(' ', '_')}_{audience}.md",
        mime="text/markdown",
    )

    with st.expander(f"Classified Items ({len(result['items'])} items)"):
        st.json(result["items"])

    with st.expander("Structured Synthesis"):
        st.json(result["synthesis"])


if __name__ == "__main__":
    main()