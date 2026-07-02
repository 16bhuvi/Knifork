"""
generator.py
------------------------------------
Core AI generation engine for Knifork.

Responsibilities
----------------
✓ Connect to Groq
✓ Generate Table of Contents
✓ Generate Chapters
✓ Retry on failures
✓ Report progress to UI
✓ Return structured chapter data
"""

import re
import time
from typing import Callable, List, Dict, Optional

from groq import Groq

from prompts import PromptTemplates


class BookGenerator:

    WORDS_PER_PAGE = 400
    WORDS_PER_CHUNK = 900

    MAX_RETRIES = 4
    RETRY_DELAY = 15

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        progress_callback: Optional[Callable] = None,
    ):

        self.client = Groq(api_key=api_key)

        self.model = model

        self.progress_callback = progress_callback

    # ---------------------------------------------------------
    # Progress
    # ---------------------------------------------------------

    def update(
        self,
        message: str,
        percent: Optional[int] = None,
    ):

        print(message)

        if self.progress_callback:

            try:

                self.progress_callback(
                    message,
                    percent
                )

            except TypeError:

                self.progress_callback(
                    message
                )

    # ---------------------------------------------------------
    # Groq Call
    # ---------------------------------------------------------

    def call_model(
        self,
        prompt: str,
        max_tokens: int = 1800,
    ) -> str:

        for attempt in range(
            self.MAX_RETRIES
        ):

            try:

                response = self.client.chat.completions.create(

                    model=self.model,

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.9,

                    max_tokens=max_tokens,

                )

                return response.choices[0].message.content.strip()

            except Exception as e:

                self.update(

                    f"Retry {attempt+1}/{self.MAX_RETRIES}: {e}"

                )

                time.sleep(
                    self.RETRY_DELAY
                )

        raise RuntimeError(
            "Maximum retries exceeded."
        )

    # ---------------------------------------------------------
    # TOC
    # ---------------------------------------------------------

    def generate_toc(
        self,
        topic: str,
        chapters: int,
    ) -> List[str]:

        self.update(
            "Generating Table of Contents...",
            5,
        )

        prompt = PromptTemplates.toc(
            topic,
            chapters,
        )

        result = self.call_model(
            prompt,
            600,
        )

        titles = []

        for line in result.splitlines():

            line = line.strip()

            if not line:
                continue

            cleaned = re.sub(
                r"^\d+[\.\)]\s*",
                "",
                line
            )

            if cleaned:

                titles.append(
                    cleaned
                )

        while len(titles) < chapters:

            titles.append(
                f"{topic} Part {len(titles)+1}"
            )

        return titles[:chapters]

    # ---------------------------------------------------------
    # Generate Single Chapter
    # ---------------------------------------------------------

    def generate_chapter(
        self,
        topic: str,
        chapter_title: str,
        chapter_number: int,
        target_words: int,
        total_chapters: int,
    ) -> str:

        chapter_text = ""

        previous_tail = ""

        chunk = 0

        while len(chapter_text.split()) < target_words:

            chunk += 1

            remaining_words = (
                target_words - len(chapter_text.split())
            )

            current_chunk_words = min(
                self.WORDS_PER_CHUNK,
                remaining_words + 150,
            )

            progress = int(
                10
                + (
                    (chapter_number - 1)
                    / total_chapters
                )
                * 80
            )

            self.update(
                f"Generating Chapter {chapter_number}/{total_chapters} "
                f"(Chunk {chunk})",
                progress,
            )

            if chunk == 1:

                prompt = PromptTemplates.first_chapter(

                    topic=topic,

                    chapter_no=chapter_number,

                    chapter_title=chapter_title,

                    words=current_chunk_words,

                )

            else:

                should_finish = (
                    remaining_words
                    <= self.WORDS_PER_CHUNK
                )

                prompt = PromptTemplates.continue_chapter(

                    topic=topic,

                    chapter_no=chapter_number,

                    chapter_title=chapter_title,

                    previous=previous_tail,

                    words=current_chunk_words,

                    conclude=should_finish,

                )

            text = self.call_model(
                prompt,
                max_tokens=1700,
            )

            if chapter_text:

                chapter_text += "\n\n"

            chapter_text += text

            previous_tail = " ".join(
                text.split()[-120:]
            )

            words_written = len(
                chapter_text.split()
            )

            self.update(

                f"Chapter {chapter_number}: "
                f"{words_written}/{target_words} words",

                progress,

            )

            time.sleep(1)

            if chunk >= 25:

                self.update(
                    "Safety stop reached (25 chunks)."
                )

                break

        return chapter_text

    # ---------------------------------------------------------
    # Generate Complete Book
    # ---------------------------------------------------------

    def generate(
        self,
        topic: str,
        pages: int,
        chapters: int = 0,
    ) -> List[Dict]:

        if not topic.strip():
            raise ValueError("Topic cannot be empty.")

        if pages <= 0:
            raise ValueError("Pages must be greater than zero.")

        # -----------------------------
        # Auto Chapter Calculation
        # -----------------------------

        if chapters <= 0:

            chapters = max(
                3,
                min(30, round(pages / 15))
            )

        total_words = pages * self.WORDS_PER_PAGE

        words_per_chapter = total_words // chapters

        self.update(
            f"Book Topic: {topic}",
            0
        )

        self.update(
            f"Target Pages: {pages}",
            1
        )

        self.update(
            f"Target Chapters: {chapters}",
            2
        )

        # -----------------------------
        # Generate TOC
        # -----------------------------

        toc = self.generate_toc(
            topic,
            chapters,
        )

        self.update(
            "Table of Contents Generated",
            8
        )

        result = []

        # -----------------------------
        # Generate Every Chapter
        # -----------------------------

        for index, chapter_title in enumerate(
            toc,
            start=1
        ):

            chapter = self.generate_chapter(

                topic=topic,

                chapter_title=chapter_title,

                chapter_number=index,

                target_words=words_per_chapter,

                total_chapters=chapters,

            )

            result.append(

                {

                    "chapter": index,

                    "title": chapter_title,

                    "content": chapter,

                    "words": len(
                        chapter.split()
                    )

                }

            )

            percent = int(

                10 +

                (index / chapters) * 85

            )

            self.update(

                f"Completed Chapter {index}/{chapters}",

                percent

            )

        total_written = sum(

            c["words"]

            for c in result

        )

        self.update(

            f"Book Completed ({total_written} words)",

            100

        )

        return result