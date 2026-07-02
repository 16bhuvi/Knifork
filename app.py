import os
import streamlit as st

from generator import BookGenerator
from doc_writer import DocumentWriter


# ----------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------

st.set_page_config(
    page_title="Knifork AI",
    page_icon="📄",
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

    st.title("Knifork")

    st.caption("AI Documentation Engine")

    st.divider()

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        help="Enter your Groq API credentials",
    )

    model = st.selectbox(
        "Model Endpoint",
        [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ],
    )

    st.divider()

    st.subheader("System Specifications")

    st.metric(
        "Engine Status",
        "Idle",
    )

    st.metric(
        "Output Protocol",
        "DOCX",
    )

    st.metric(
        "Provider API",
        "Groq Console",
    )

    st.divider()

    if st.button(
        "Clear Console Logs",
        use_container_width=True,
    ):
        st.session_state.logs = []
        st.session_state.progress = 0
        st.session_state.generated_file = None
        st.rerun()

# ----------------------------------------------------------
# MAIN HEADER
# ----------------------------------------------------------

st.title("Knifork AI // Documentation Pipeline")

st.markdown(
    """
High-density document generation platform powered by Groq.
Compiles complete books, structured reports, case studies, and research publications.
"""
)

st.divider()

# ----------------------------------------------------------
# INPUT FORM
# ----------------------------------------------------------

left, right = st.columns(2)

with left:

    topic = st.text_input(
        "Document Topic",
        placeholder="Example: Netflix Global Content Strategy",
    )

    pages = st.number_input(
        "Target Page Count",
        min_value=5,
        max_value=500,
        value=50,
        step=5,
    )

with right:

    chapters = st.number_input(
        "Chapter Count (0 = Auto)",
        min_value=0,
        max_value=50,
        value=0,
        step=1,
    )

    output_type = st.selectbox(
        "Target File Format",
        [
            "DOCX",
        ],
    )

st.markdown("### Model Directives")

description = st.text_area(
    "Additional Instructions",
    label_visibility="collapsed",
    height=140,
    placeholder="""
Example directives:
- Write in an academic, analytical style.
- Include concrete real-world case studies.
- Use precise professional terminology.
- Establish clean hierarchical subsections.
- Prevent textual repetition and filler content.
""",
)

st.divider()

# ----------------------------------------------------------
# GENERATE BUTTON
# ----------------------------------------------------------

generate = st.button(
    "Initialize Generation Pipeline",
    use_container_width=True,
)

st.divider()

# ----------------------------------------------------------
# PROGRESS AREA
# ----------------------------------------------------------

st.subheader("Pipeline Execution Status")

progress_placeholder.progress(
    st.session_state.progress
)

status_placeholder.info(
    "Awaiting system initialization..."
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

    status_placeholder.info("Initializing engine thread...")

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
            "Compiling document into DOCX format..."
        )

        output_file = writer.create_document(
            topic=topic,
            chapters=chapters_data,
        )

        st.session_state.generated_file = output_file

        progress_placeholder.progress(100)

        status_placeholder.success(
            "Document Compiled Successfully."
        )

        # -----------------------------------------
        # Statistics
        # -----------------------------------------

        total_words = sum(
            chapter["words"]
            for chapter in chapters_data
        )

        total_chapters = len(chapters_data)

        st.divider()

        st.subheader("Compilation Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Words",
                f"{total_words:,}"
            )

        with col2:
            st.metric(
                "Chapters Written",
                total_chapters
            )

        with col3:
            st.metric(
                "Target Pages",
                pages
            )

        st.divider()

        st.success(
            f"Document saved to:\n\n{output_file}"
        )

        with open(output_file, "rb") as file:

            st.download_button(

                label="Download Generated Document (DOCX)",

                data=file,

                file_name=os.path.basename(output_file),

                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",

                use_container_width=True,

            )

    except Exception as e:

        progress_placeholder.progress(0)

        status_placeholder.error("Generation Pipeline Failed")

        st.exception(e)