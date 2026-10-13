"""
Streamlit UI for the Resume ↔ Job Description Matcher.
Run with: streamlit run app.py
"""
import streamlit as st

from agent import analyze_resume
from utils.file_parser import extract_text

# ---------- Config ----------
GITHUB_URL = "https://github.com/your-username/resume-matcher"  # <- change me

st.set_page_config(
    page_title="Resume Matcher",
    page_icon=None,
    layout="wide",
)

# ---------- Header ----------
st.title("Resume to Job Description Matcher")
st.caption(
    "Upload or paste a resume and a job description. Get a match score, "
    "skill gaps, and rewritten resume bullets in seconds."
)

# ---------- Inputs ----------
col1, col2 = st.columns(2)

# ----- Resume column -----
with col1:
    st.subheader("Resume")

    resume_method = st.radio(
        "How do you want to provide your resume?",
        ["Upload file", "Paste text"],
        horizontal=True,
        key="resume_method",
    )

    resume_text = ""

    if resume_method == "Upload file":
        resume_file = st.file_uploader(
            "Upload your resume (PDF or TXT)",
            type=["pdf", "txt"],
            key="resume_file",
        )
        if resume_file is not None:
            extracted = extract_text(resume_file)
            if extracted.startswith("[Error"):
                st.error(extracted)
            elif not extracted.strip():
                st.warning("No text could be extracted from this file.")
            else:
                st.success(f"Extracted {len(extracted):,} characters from {resume_file.name}")
                with st.expander("Preview extracted text"):
                    st.text(extracted[:1000] + ("..." if len(extracted) > 1000 else ""))
                resume_text = extracted
    else:
        resume_text = st.text_area(
            "Paste your resume text",
            height=320,
            placeholder="Paste your resume here...",
        )

# ----- Job Description column -----
with col2:
    st.subheader("Job Description")

    jd_method = st.radio(
        "How do you want to provide the job description?",
        ["Upload file", "Paste text"],
        horizontal=True,
        key="jd_method",
    )

    jd_text = ""

    if jd_method == "Upload file":
        jd_file = st.file_uploader(
            "Upload the job description (PDF or TXT)",
            type=["pdf", "txt"],
            key="jd_file",
        )
        if jd_file is not None:
            extracted = extract_text(jd_file)
            if extracted.startswith("[Error"):
                st.error(extracted)
            elif not extracted.strip():
                st.warning("No text could be extracted from this file.")
            else:
                st.success(f"Extracted {len(extracted):,} characters from {jd_file.name}")
                with st.expander("Preview extracted text"):
                    st.text(extracted[:1000] + ("..." if len(extracted) > 1000 else ""))
                jd_text = extracted
    else:
        jd_text = st.text_area(
            "Paste the job description",
            height=320,
            placeholder="Paste the job description here...",
        )

# ---------- Analyze ----------
st.divider()
analyze_clicked = st.button("Analyze Match", type="primary", use_container_width=True)

if analyze_clicked:
    if not resume_text.strip() or not jd_text.strip():
        st.warning("Please provide both a resume and a job description.")
    else:
        with st.spinner("Analyzing..."):
            st.session_state["result"] = analyze_resume(resume_text, jd_text)

# ---------- Results ----------
if "result" in st.session_state:
    result = st.session_state["result"]

    if "error" in result:
        st.error(result["error"])
    else:
        st.divider()
        st.header("Results")

        # --- Score + verdict ---
        score = int(result.get("match_score", 0))
        score = max(0, min(100, score))

        if score >= 80:
            tier_label = "Strong match"
            tier_note = "Your resume aligns well with this role."
            tier_icon = ":green[●]"
        elif score >= 60:
            tier_label = "Good match"
            tier_note = "A few gaps, but worth applying."
            tier_icon = ":blue[●]"
        elif score >= 40:
            tier_label = "Partial match"
            tier_note = "Consider tailoring your resume before applying."
            tier_icon = ":orange[●]"
        else:
            tier_label = "Low match"
            tier_note = "Significant gaps for this role."
            tier_icon = ":red[●]"

        with st.container(border=True):
            score_col, verdict_col = st.columns([1, 3])

            with score_col:
                st.metric("Match Score", f"{score}%")

            with verdict_col:
                st.markdown(f"### {tier_icon} {tier_label}")
                st.caption(tier_note)

            st.progress(score / 100)

        # --- Explanation ---
        with st.container(border=True):
            st.markdown("**Why**")
            st.write(result.get("explanation", "No explanation provided."))

        # --- Skills ---
        skill_col1, skill_col2 = st.columns(2)

        with skill_col1:
            with st.container(border=True):
                matching = result.get("matching_skills", [])
                st.markdown(f"**Matching Skills** · {len(matching)}")
                if matching:
                    for s in matching:
                        st.markdown(f"- {s}")
                else:
                    st.caption("None detected.")

        with skill_col2:
            with st.container(border=True):
                missing = result.get("missing_skills", [])
                st.markdown(f"**Missing Skills** · {len(missing)}")
                if missing:
                    for s in missing:
                        st.markdown(f"- {s}")
                else:
                    st.caption("None — great fit!")

        # --- Rewritten bullets ---
        st.subheader("Rewritten Resume Bullets")
        st.caption("Tailored to this job description. Copy any bullet into your resume.")
        bullets = result.get("rewritten_bullets", [])
        if bullets:
            for i, b in enumerate(bullets, 1):
                st.markdown(f"**{i}.** {b}")
        else:
            st.caption("No rewrites were suggested.")

# ---------- Footer ----------
st.divider()
st.caption(f"Built with Streamlit + Groq · [View on GitHub]({GITHUB_URL})")