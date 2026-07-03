# Knifork AI - Book & Report Generator 

Knifork is a modern Streamlit-based web application that generates professional, long-form documents, reports, and books using AI. 

Powered by Groq's high-speed LLMs, the application dynamically designs table of contents, plans chapters, and writes content with high narrative continuity and minimal repetition.

## Features 
- **Bulk Content Generation**: Auto-calculates chapter target words and generates long-form text.
- **Dynamic Table of Contents**: Automatically designs the book's structure based on your topic.
- **Professional Formatting**: Exports directly to a fully-styled DOCX file.
- **Interactive UI**: Real-time progress bar, live generation status, and real-time logs.
- **Continuous Generation**: Writes chapters chunk-by-chunk to respect model context and rate limits.

## Installation 

1. **Clone the Repository**:
   ```bash
   git clone <your-repository-url>
   cd knifork
   ```

2. **Set up Virtual Environment**:
   ```bash
   uv venv
   # On Windows (PowerShell):
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run the Streamlit App**:
   ```bash
   streamlit run app.py
   ```

## Usage 📖
1. Enter your **Groq API Key** in the sidebar.
2. Select your desired AI **Model**.
3. Provide your report **Topic** and desired number of **Pages**.
4. Add any **Additional Instructions** (e.g. "Use professional language", "Include headings").
5. Click **Generate Report** and watch the progress in real-time. Once completed, download your styled `.docx` file!

## License 📄
Mozilla Public License 2.0
      
