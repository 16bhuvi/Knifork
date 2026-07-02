"""
prompts.py
------------------------------------

Centralized prompt templates used by Knifork.

This keeps all AI prompts in one place so they are
easy to edit without touching generator.py.
"""


class PromptTemplates:

    @staticmethod
    def toc(topic: str, chapters: int) -> str:
        return f"""
You are a professional author, researcher, professor, business consultant,
technical writer and editor.

Your task is to create a professional Table of Contents for a complete book.

BOOK TOPIC
----------
{topic}

Requirements

- Generate EXACTLY {chapters} chapters.
- Chapters should follow a logical flow.
- Cover beginner to advanced concepts.
- Avoid duplicate chapter names.
- Make chapter titles professional.
- Keep titles concise.
- Do not include introductions or explanations.

Return ONLY the chapter titles in this format:

1. Chapter Title
2. Chapter Title
3. Chapter Title

Nothing else.
"""

    @staticmethod
    def first_chapter(
        topic: str,
        chapter_no: int,
        chapter_title: str,
        words: int,
    ) -> str:

        return f"""
You are writing a professional book.

BOOK TITLE
----------
{topic}

Write

Chapter {chapter_no}

Title:
{chapter_title}

Requirements

- Write approximately {words} words.
- Write naturally.
- Use Markdown headings where appropriate.
- Use paragraphs.
- Explain concepts in detail.
- Include examples.
- Include facts where appropriate.
- Avoid repeating information.
- Do NOT summarize the entire book.
- Do NOT conclude the chapter.
- End naturally so another continuation prompt can continue writing.

Write only the chapter.
"""

    @staticmethod
    def continue_chapter(
        topic: str,
        chapter_no: int,
        chapter_title: str,
        previous: str,
        words: int,
        conclude: bool = False,
    ) -> str:

        ending_instruction = (
            """
Finish the chapter with a concise conclusion.

Do not start another chapter.
"""
            if conclude
            else
            """
Continue writing naturally.

Do NOT conclude the chapter.
"""
        )

        return f"""
Continue writing the same chapter.

BOOK
----
{topic}

Chapter {chapter_no}

Title
-----
{chapter_title}

Previous Ending
---------------
{previous}

Requirements

- Write approximately {words} words.
- Continue exactly where the previous text stopped.
- Never repeat previously written content.
- Maintain the same tone and writing style.
- Use Markdown headings when needed.
- Use paragraphs.
- Add examples whenever useful.
- Avoid filler text.

{ending_instruction}

Return only the continuation.
"""