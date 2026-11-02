import os
import re
import subprocess
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import soundfile as sf
import torch
from TTS.api import TTS

# XTTS v2 всегда генерирует звук с частотой 24 кГц
XTTS_SAMPLE_RATE = 24000


class TTSEngine:
    # XTTS v2 уверенно работает с фрагментами до ~250 символов,
    # длинные тексты нужно разбивать и склеивать
    MAX_CHARS_PER_CHUNK = 250
    # Встроенные мужские голоса XTTS v2 (используется первый доступный)
    MALE_SPEAKERS = ['Randall Hood', 'Damien Black', 'Andrew Chipper', 'Craig Gutsy']

    def __init__(self, language: str = 'ru'):
        self.language = language
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f'🚀 Используемое устройство: {self.device.upper()}')

        print('⏳ Загрузка модели XTTS v2 (первый запуск может занять несколько минут)...')
        self.tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2')
        self.tts.to(self.device)

        self.available_speakers = list(getattr(self.tts, 'speakers', []) or [])
        self.speaker = next((s for s in self.MALE_SPEAKERS if s in self.available_speakers), None)
        if self.speaker:
            print(f'🎤 Встроенный голос по умолчанию: {self.speaker}')

    def _split_text(self, text: str):
        """Разбивает текст на фрагменты, подходящие для XTTS v2."""
        sentences = re.split(r'(?<=[.!?…])\s+', text.strip())
        chunks = []
        current = ''
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 > self.MAX_CHARS_PER_CHUNK:
                if current:
                    chunks.append(current)
                    current = ''
                if len(sentence) > self.MAX_CHARS_PER_CHUNK:
                    chunks.extend(self._split_long_sentence(sentence))
                    continue
            current = f'{current} {sentence}'.strip()
        if current:
            chunks.append(current)
        return chunks

    def _split_long_sentence(self, sentence: str):
        parts = []
        while len(sentence) > self.MAX_CHARS_PER_CHUNK:
            cut = sentence.rfind(' ', 0, self.MAX_CHARS_PER_CHUNK)
            if cut <= 0:
                cut = self.MAX_CHARS_PER_CHUNK
            parts.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if sentence:
            parts.append(sentence)
        return parts

    def synthesize(
        self,
        text: str,
        output_path: str,
        reference_audio: Optional[str] = None,
        language: Optional[str] = None,
        speaker: Optional[str] = None,
        progress_cb: Optional[Callable[[int, int], None]] = None,
    ):
        kwargs = {'language': language or self.language}

        # Приоритет: референс (клонирование) > выбранный голос > голос по умолчанию
        if reference_audio and os.path.exists(reference_audio):
            kwargs['speaker_wav'] = reference_audio
            print(f'🎭 Клонирование голоса из: {reference_audio}')
        else:
            chosen = speaker or self.speaker
            if not chosen:
                raise RuntimeError(
                    'Не найден голос: загрузите референс или выберите встроенный голос.'
                )
            kwargs['speaker'] = chosen
            print(f'🎤 Используется голос: {chosen}')

        chunks = self._split_text(text)
        print(f'✂️  Текст разбит на {len(chunks)} фрагмент(ов)')

        if len(chunks) == 1:
            self.tts.tts_to_file(text=chunks[0], file_path=output_path, **kwargs)
            if progress_cb:
                progress_cb(1, 1)
            return

        audio_parts = []
        for i, chunk in enumerate(chunks, 1):
            print(f'  🔊 Генерация фрагмента {i}/{len(chunks)}...')
            audio_parts.append(np.asarray(self.tts.tts(text=chunk, **kwargs), dtype=np.float32))
            if progress_cb:
                progress_cb(i, len(chunks))

        # Склеиваем фрагменты с короткой паузой на стыках
        pause = np.zeros(int(XTTS_SAMPLE_RATE * 0.15), dtype=np.float32)
        merged = []
        for i, part in enumerate(audio_parts):
            if i > 0:
                merged.append(pause)
            merged.append(part)
        self._write_audio(np.concatenate(merged), output_path)

    def _write_audio(self, samples: np.ndarray, output_path: str):
        out = Path(output_path)
        if out.suffix.lower() == '.mp3':
            tmp_wav = out.with_name(out.stem + '.tmp.wav')
            sf.write(tmp_wav, samples, XTTS_SAMPLE_RATE)
            subprocess.run(
                ['ffmpeg', '-y', '-i', str(tmp_wav), '-codec:a', 'libmp3lame', '-b:a', '192k', str(out)],
                check=True,
                capture_output=True,
            )
            tmp_wav.unlink()
        else:
            sf.write(out, samples, XTTS_SAMPLE_RATE)
