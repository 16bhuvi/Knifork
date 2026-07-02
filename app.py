import os
import streamlit as st

from generator import BookGenerator
from doc_writer import DocumentWriter


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Knifork AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------
# LOAD CUSTOM CSS
# ----------------------------------------------------------

def load_css():
    if os.path.exists("styles.css"):
        with open("styles.css", "r", encoding="utf-8") as css:
            st.markdown(
                f"<style>{css.read()}</style>",
                unsafe_allow_html=True,
            )


load_css()


# ----------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------

if "logs" not in st.session_state:
    st.session_state.logs = []

if "progress" not in st.session_state:
    st.session_state.progress = 0

if "generated_file" not in st.session_state:
    st.session_state.generated_file = None

if "running" not in st.session_state:
    st.session_state.running = False


# ----------------------------------------------------------
# PLACEHOLDERS
# ----------------------------------------------------------

progress_placeholder = st.empty()

status_placeholder = st.empty()

logs_placeholder = st.empty()


# ----------------------------------------------------------
# CALLBACK FROM GENERATOR
# ----------------------------------------------------------

def progress_callback(message, percent=None):

    if percent is not None:

        st.session_state.progress = percent

        progress_placeholder.progress(percent)

    st.session_state.logs.append(message)

    status_placeholder.info(message)

    logs_placeholder.code(
        "\n".join(st.session_state.logs[-25:]),
        language="text",
    )


# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------

with st.sidebar:

    st.title("📚 Knifork")

    st.caption("AI Book & Report Generator")

    st.divider()

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Paste your Groq API key",
    )

    model = st.selectbox(
        "Model",
        [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ],
    )

    st.divider()

    st.subheader("Statistics")

    st.metric(
        "Status",
        "Ready",
    )

    st.metric(
        "Output",
        "DOCX",
    )

    st.metric(
        "Provider",
        "Groq",
    )

    st.divider()

    if st.button(
        "🗑 Clear Logs",
        use_container_width=True,
    ):
        st.session_state.logs = []
        st.session_state.progress = 0
        st.session_state.generated_file = None
        st.rerun()

# ----------------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------------

st.title("📚 Knifork AI Report Generator")

st.markdown(
    """
Generate professional:

- 📚 Books
- 📄 Reports
- 🎓 Research Papers
- 📊 Case Studies
- 📖 Documentation

using Groq AI.
"""
)

st.divider()

# ----------------------------------------------------------
# INPUT FORM
# ----------------------------------------------------------

left, right = st.columns(2)

with left:

    topic = st.text_input(
        "📚 Topic",
        placeholder="Example: Netflix Business Strategy",
    )

    pages = st.number_input(
        "📄 Number of Pages",
        min_value=5,
        max_value=500,
        value=50,
        step=5,
    )

with right:

    chapters = st.number_input(
        "📑 Chapters (0 = Auto)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
    )

    output_type = st.selectbox(
        "📂 Output Format",
        [
            "DOCX",
        ],
    )

st.markdown("### 📝 Additional Instructions")

description = st.text_area(
    "",
    height=140,
    placeholder="""
Example:

Write an academic report.

Include real-world examples.

Use professional language.

Include headings and subheadings.

Avoid repetition.

Write in detailed style.
""",
)

st.divider()

# ----------------------------------------------------------
# GENERATE BUTTON
# ----------------------------------------------------------

generate = st.button(
    "🚀 Generate Report",
    use_container_width=True,
)

st.divider()

# ----------------------------------------------------------
# PROGRESS AREA
# ----------------------------------------------------------

st.subheader("Generation Progress")

progress_placeholder.progress(
    st.session_state.progress
)

status_placeholder.info(
    "Waiting to start..."
)

logs_placeholder.code(
    "\n".join(st.session_state.logs),
    language="text",
)

st.divider()

# ----------------------------------------------------------
# GENERATE
# ----------------------------------------------------------

if generate:

    if not topic.strip():

        st.error("Please enter a topic.")

        st.stop()

    if not api_key.strip():

        st.error("Please enter your Groq API Key.")

        st.stop()

    st.session_state.logs = []

    st.session_state.progress = 0

    st.session_state.generated_file = None

    progress_placeholder.progress(0)

    status_placeholder.info("Initializing AI...")

    try:

        generator = BookGenerator(
            api_key=api_key,
            model=model,
            progress_callback=progress_callback,
        )

        writer = DocumentWriter()

        # -----------------------------------------
        # Generate Book
        # -----------------------------------------

        chapters_data = generator.generate(
            topic=topic,
            pages=pages,
            chapters=chapters,
        )

        progress_placeholder.progress(95)

        status_placeholder.success(
            "Writing DOCX document..."
        )

        output_file = writer.create_document(
            topic=topic,
            chapters=chapters_data,
        )

        st.session_state.generated_file = output_file

        progress_placeholder.progress(100)

        status_placeholder.success(
            "Report Generated Successfully!"
        )

        st.balloons()

        # -----------------------------------------
        # Statistics
        # -----------------------------------------

        total_words = sum(
            chapter["words"]
            for chapter in chapters_data
        )

        total_chapters = len(chapters_data)

        st.divider()

        st.subheader("Generation Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Words",
                f"{total_words:,}"
            )

        with col2:
            st.metric(
                "Chapters",
                total_chapters
            )

        with col3:
            st.metric(
                "Pages",
                pages
            )

        st.divider()

        st.success(
            f"Document saved to:\n\n{output_file}"
        )

        with open(output_file, "rb") as file:

            st.download_button(

                label="📥 Download DOCX",

                data=file,

                file_name=os.path.basename(output_file),

                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",

                use_container_width=True,

            )

    except Exception as e:

        progress_placeholder.progress(0)

        status_placeholder.error("Generation Failed")

        st.exception(e)