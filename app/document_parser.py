import re
from pathlib import Path
from docx import Document
from PyPDF2 import PdfReader


class DocumentParser:
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.docx', '.pdf'}

    def extract_text(self, file_path: Path) -> str:
        extension = file_path.suffix.lower()
        if extension in {'.txt', '.md'}:
            try:
                text = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # Старые русские файлы часто в cp1251
                text = file_path.read_text(encoding='cp1251')
            if extension == '.md':
                text = self._clean_markdown(text)
            return text
        elif extension == '.docx':
            doc = Document(file_path)
            return '\n'.join([p.text for p in doc.paragraphs])
        elif extension == '.pdf':
            reader = PdfReader(file_path)
            return '\n'.join([page.extract_text() or '' for page in reader.pages])
        else:
            raise ValueError(f'Неподдерживаемый формат: {extension}')

    @staticmethod
    def _clean_markdown(text: str) -> str:
        """Убирает разметку Markdown, оставляя только читаемый текст."""
        # Код-блоки убираем целиком
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # Картинки убираем, ссылки [текст](url) -> текст
        text = re.sub(r'!\[([^\]]*)\]\([^)]*\)', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
        # Заголовки, списки, цитаты
        text = re.sub(r'(?m)^\s{0,3}#{1,6}\s*', '', text)
        text = re.sub(r'(?m)^\s{0,3}([-*+]|\d+\.)\s+', '', text)
        text = re.sub(r'(?m)^\s*>+\s?', '', text)
        # Горизонтальные линии и разделители таблиц
        text = re.sub(r'(?m)^\s{0,3}([-*_])\s*(\1\s*){2,}$', '', text)
        text = re.sub(r'(?m)^\s*\|?[-:]+(\|[-:]+)+\|?\s*$', '', text)
        text = text.replace('|', ' ')
        # Жирный, курсив, зачёркнутый, инлайн-код
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'~~([^~]+)~~', r'\1', text)
        text = re.sub(r'\*([^*\n]+)\*', r'\1', text)
        text = re.sub(r'_([^_\n]+)_', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # HTML-теги и лишние пустые строки
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
