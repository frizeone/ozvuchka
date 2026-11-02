import time
from pathlib import Path

import gradio as gr

from config import Config
from document_parser import DocumentParser
from tts_engine import TTSEngine

# Языки, которые поддерживает XTTS v2
LANGUAGES = ['ru', 'en', 'de', 'es', 'fr', 'it', 'pt', 'pl', 'tr', 'nl', 'cs', 'ar', 'zh-cn', 'ja', 'hu', 'ko', 'hi']

config = Config()
parser = DocumentParser()

# Модель загружается один раз при старте контейнера (на GPU)
engine = TTSEngine(language=config.language)


def extract_from_doc(file):
    """Извлекает текст из загруженного документа и подставляет его в текстовое поле."""
    if not file:
        return ''
    path = getattr(file, 'name', None) or file
    try:
        text = parser.extract_text(Path(path))
        return text if text else ''
    except Exception as e:
        raise gr.Error(f'Не удалось прочитать документ: {e}')


def generate(text, speaker, reference, language, fmt, progress=gr.Progress()):
    """Озвучивает текст и возвращает готовый аудиофайл."""
    text = (text or '').strip()
    if not text:
        raise gr.Error('Введите текст или загрузите документ.')

    out_path = f'/tmp/ozvuchka_{time.strftime("%Y%m%d_%H%M%S")}.{fmt}'

    def cb(i, total):
        progress((i - 1) / max(total, 1), desc=f'Генерация фрагмента {i}/{total}...')

    try:
        engine.synthesize(
            text=text,
            output_path=out_path,
            reference_audio=reference or None,
            language=language,
            speaker=speaker,
            progress_cb=cb,
        )
    except Exception as e:
        raise gr.Error(f'Ошибка генерации: {e}')

    size_mb = Path(out_path).stat().st_size / (1024 * 1024)
    return out_path, f'✅ Готово! {len(text)} символов, файл {size_mb:.1f} МБ.'


with gr.Blocks(
    title='Озвучка документов — XTTS v2',
    theme=gr.themes.Soft(),
    analytics_enabled=False,
) as demo:
    gr.Markdown(
        f"""
        # 🎙️ Озвучка текста и документов
        Coqui XTTS v2 · устройство: **{engine.device.upper()}**
        Загрузите документ или вставьте текст, выберите голос и нажмите «Озвучить».
        """
    )

    with gr.Row():
        with gr.Column(scale=3):
            doc = gr.File(
                label='📄 Загрузить документ (.txt, .md, .docx, .pdf) — текст подставится ниже',
                file_types=['.txt', '.md', '.docx', '.pdf'],
            )
            text = gr.Textbox(
                label='Текст для озвучивания',
                lines=14,
                placeholder='Вставьте текст сюда или загрузите документ выше...',
            )
        with gr.Column(scale=2):
            speaker = gr.Dropdown(
                label=f'🎤 Встроенный голос (по умолчанию: {engine.speaker})',
                choices=engine.available_speakers,
                value=engine.speaker,
            )
            gr.Markdown(
                '💡 Встроенные голоса на русском звучат с акцентом. '
                'Если ничего не выбирать — используется голос по умолчанию. '
                'Для естественного звучания запишите или загрузите референс ниже — голос будет склонирован.'
            )
            reference = gr.Audio(
                label='🎭 Референс голоса для клонирования (5–15 сек чистого голоса, необязательно)',
                type='filepath',
                sources=['upload', 'microphone'],
            )
            language = gr.Dropdown(label='🌍 Язык', choices=LANGUAGES, value=config.language)
            fmt = gr.Radio(label='💾 Формат файла', choices=['wav', 'mp3'], value='wav')

    btn = gr.Button('🔊 Озвучить', variant='primary')
    audio_out = gr.Audio(label='Результат', type='filepath', interactive=False)
    status = gr.Textbox(label='Статус', interactive=False, show_label=False)

    doc.change(extract_from_doc, doc, text)
    btn.click(generate, [text, speaker, reference, language, fmt], [audio_out, status])

# Очередь из одного запроса — чтобы не перегружать видеокарту
demo.queue(max_size=8, default_concurrency_limit=1)
demo.launch(server_name='0.0.0.0', server_port=7860)
