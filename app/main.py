import sys
from pathlib import Path

from tts_engine import TTSEngine
from document_parser import DocumentParser
from config import Config


def main():
    config = Config()
    parser = DocumentParser()
    tts = TTSEngine(language=config.language)

    input_dir = Path(config.input_dir)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    supported_extensions = {'.txt', '.md', '.docx', '.pdf'}
    documents = sorted(
        (f for f in input_dir.iterdir() if f.suffix.lower() in supported_extensions),
        key=lambda p: p.name,
    )

    if not documents:
        print(f'❌ В папке {input_dir} не найдено файлов .txt, .md, .docx или .pdf')
        sys.exit(1)

    print(f'📚 Найдено документов: {len(documents)}\n')

    for i, doc_path in enumerate(documents, 1):
        print(f'[{i}/{len(documents)}] Обработка: {doc_path.name}')
        try:
            text = parser.extract_text(doc_path)
            if not text.strip():
                print('⚠️  Документ пуст, пропуск.\n')
                continue

            output_path = output_dir / f'{doc_path.stem}.{config.output_format}'
            tts.synthesize(
                text=text,
                output_path=str(output_path),
                reference_audio=config.reference_audio if config.reference_audio else None,
            )
            print(f'✅ Сохранено: {output_path.name}\n')
        except Exception as e:
            print(f'❌ Ошибка с {doc_path.name}: {e}\n')

    print('🎉 Готово! Проверьте папку output/')


if __name__ == '__main__':
    main()
