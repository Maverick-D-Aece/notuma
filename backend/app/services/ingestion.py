import re
import io
from typing import List, Dict, Any
from docx import Document
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

class IngestionService:
    @staticmethod
    def parse_txt(content: bytes) -> str:
        return content.decode('utf-8')

    @staticmethod
    def parse_docx(content: bytes) -> str:
        doc = Document(io.BytesIO(content))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def parse_epub(content: bytes) -> str:
        book = epub.read_epub(io.BytesIO(content))
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                chapters.append(soup.get_text())
        return "\n".join(chapters)

    @staticmethod
    def split_into_chapters(text: str) -> List[Dict[str, Any]]:
        # Heuristic splitting by common chapter indicators
        chapter_pattern = re.compile(r'(Chapter\s+\d+|CHAPTER\s+\d+|[IVXLCDM]+\.)', re.IGNORECASE)
        splits = list(chapter_pattern.finditer(text))

        if not splits:
            return [{"title": "Chapter 1", "content": text, "order": 1}]

        chapters = []
        for i in range(len(splits)):
            start = splits[i].start()
            end = splits[i+1].start() if i+1 < len(splits) else len(text)
            title = splits[i].group(0)
            content = text[start:end].strip()
            chapters.append({"title": title, "content": content, "order": i+1})

        return chapters

    @staticmethod
    def split_into_scenes(chapter_content: str) -> List[Dict[str, Any]]:
        # Scene splitting based on common separators like *** or ### or double blank lines
        scene_separators = [r'\*\*\*+', r'###+', r'\n\s*\n\s*\n']
        pattern = '|'.join(scene_separators)
        scenes_text = re.split(pattern, chapter_content)

        scenes = []
        for i, text in enumerate(scenes_text):
            if text.strip():
                scenes.append({"text": text.strip(), "order": i+1})

        return scenes
