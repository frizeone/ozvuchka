<div align="center">

# 🎙️ Озвучка · Ozvuchka

**Локальное озвучивание текста и документов с клонированием голоса**
**Local text & document voice-over with voice cloning**

Работает на [Coqui XTTS v2](https://github.com/coqui-ai/TTS) с аппаратным ускорением NVIDIA GPU,
в Docker, с удобным веб-интерфейсом на Gradio.
*Powered by [Coqui XTTS v2](https://github.com/coqui-ai/TTS), NVIDIA GPU acceleration, Docker, Gradio web UI.*

[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-✔-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![CUDA](https://img.shields.io/badge/NVIDIA-CUDA-76B900?style=flat-square&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![TTS](https://img.shields.io/badge/Coqui%20TTS-0.22.0-8A2BE2?style=flat-square)](https://github.com/coqui-ai/TTS)
[![Gradio](https://img.shields.io/badge/Gradio-4.44.1-F97316?style=flat-square)](https://www.gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**🇷🇺 Русская версия ниже · 🇬🇧 English version below**

*Вставьте текст — получите речь. Загрузите документ — получите озвучку. Запишите 10 секунд своего голоса — и модель заговорит вашим голосом.*
*Paste text — get speech. Upload a document — get a voice-over. Record 10 seconds of your voice — and the model will speak in your voice.*

</div>

---

# 🇷🇺 Русский

## ✨ Возможности

- 🗣️ **Клонирование голоса** — загрузите или запишите с микрофона референс 5–15 секунд, и модель заговорит этим голосом
- 📄 **Поддержка документов** — `.txt`, `.md` (разметка автоматически вычищается), `.docx`, `.pdf`
- 🌍 **17 языков** — русский, английский, немецкий, испанский, французский и другие
- ⚡ **Ускорение на GPU** — генерация на видеокарте NVIDIA в 10–20 раз быстрее, чем на CPU
- 📑 **Длинные тексты** — документ автоматически разбивается на фрагменты и склеивается с паузами
- 💾 **Форматы** — `WAV` и `MP3`
- 🖥️ **Веб-интерфейс** — ничего не нужно запускать вручную, всё делается в браузере
- 📦 **Пакетный режим** — озвучивание целой папки документов одной командой

## 🚀 Быстрый старт

### Требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) для Windows с бэкендом **WSL2**
- *(Опционально, но крайне рекомендуется)* Видеокарта **NVIDIA** с актуальным драйвером
- 8+ ГБ свободного места (образ + модель)

### Запуск

```powershell
docker compose up -d --build
```

Затем откройте в браузере: **http://localhost:7860** 🌐

Первый запуск скачивает модель XTTS v2 (~2 ГБ) и собирает образ — займёт 10–20 минут.
Модель и все слои кэшируются, поэтому последующие запуски занимают меньше минуты.

```powershell
docker compose logs -f ui   # логи (должно быть: 🚀 Используемое устройство: CUDA)
docker compose down         # остановить
docker compose up -d        # запустить снова (без пересборки)
```

## 🖥️ Веб-интерфейс

1. **Текст** — вставьте в поле или загрузите документ: текст подставится автоматически
2. **Голос**
   - выберите встроенный голос из списка, **или**
   - загрузите/запишите референс 5–15 сек чистого голоса — голос будет склонирован
     (референс имеет приоритет над встроенным голосом)
   - если ничего не выбрано — автоматически используется **голос по умолчанию**
     (мужской встроенный голос XTTS v2)
3. **Язык и формат** — `ru` по умолчанию, `wav` или `mp3`
4. Нажмите **«🔊 Озвучить»** — у длинных текстов будет виден прогресс по фрагментам
5. Прослушайте и скачайте результат прямо на странице

> 💡 Встроенные голоса XTTS v2 — англоязычные и на русском звучат с акцентом.
> Для естественного русского звучания используйте клонирование голоса.

## 📦 Пакетный режим

Озвучивание целой папки документов без веб-интерфейса:

1. Положите документы в папку `input\`
2. *(Опционально)* Положите запись голоса 5–15 сек в `reference\male_voice.wav`
3. Выполните:

```powershell
docker compose --profile batch run --rm batch
```

Готовые файлы появятся в папке `output\`.

## 🗂️ Структура проекта

```text
Озвучка/
├── Dockerfile                 # образ: python:3.10-slim + ffmpeg + PyTorch CUDA
├── docker-compose.yml         # сервисы: ui (веб) и batch (пакетный режим)
├── requirements.txt           # зависимости с прибитыми совместимыми версиями
├── app/
│   ├── ui.py                  # веб-интерфейс на Gradio
│   ├── main.py                # пакетный режим
│   ├── tts_engine.py          # движок XTTS v2: разбивка текста, склейка, прогресс
│   ├── document_parser.py     # чтение .txt / .md / .docx / .pdf
│   └── config.py              # настройки из переменных окружения
├── input/                     # 📥 документы для пакетного режима
├── output/                    # 📤 результат пакетного режима
└── reference/                 # 🎭 референс голоса для клонирования
```

## ⚙️ Конфигурация

Настройки задаются в `docker-compose.yml` через переменные окружения:

| Переменная        | Значение                    | Описание                                  |
|-------------------|-----------------------------|-------------------------------------------|
| `LANGUAGE`        | `ru`                        | Язык по умолчанию                         |
| `REFERENCE_AUDIO` | `/reference/male_voice.wav` | Референс голоса для пакетного режима      |
| `OUTPUT_FORMAT`   | `wav`                       | Формат для пакетного режима (`wav`/`mp3`) |
| `SAMPLE_RATE`     | `24000`                     | XTTS v2 работает на 24 кГц                |

## 🧠 Как это работает

- **Генерация** — нейросеть XTTS v2 генерирует речь с частотой 24 кГц прямо на видеокарте
- **Клонирование голоса** — модель извлекает эмбеддинг голоса из референса и воспроизводит его тембр на любом языке
- **Длинные тексты** — текст разбивается на фрагменты до 250 символов, каждый генерируется отдельно,
  затем фрагменты склеиваются с короткими паузами на стыках
- **Markdown** — перед озвучкой из `.md`-файлов удаляются заголовки, ссылки, код-блоки и прочая разметка
- **Кэш модели** — модель (~2 ГБ) хранится в Docker-томе `tts-models` и не скачивается повторно

## 🛠️ Устранение неполадок

| Проблема | Решение |
|----------|---------|
| В логе `CPU` вместо `CUDA` | Видеокарта не пробросилась: обновите драйвер NVIDIA и убедитесь, что включён WSL2-бэкенд Docker Desktop |
| Нет видеокарты — нужен CPU | Удалите блоки `deploy` у сервисов `ui` и `batch` в `docker-compose.yml` |
| В поле голоса ничего не выбрано | Не проблема: используется голос по умолчанию (мужской встроенный голос XTTS v2) |
| Ошибка `\r: command not found` | Файлы должны быть с окончаниями LF (в репозитории настроен `.gitattributes`) |
| Проверить GPU в контейнере | `docker compose run --rm ui python -c "import torch; print(torch.cuda.is_available())"` |

---

# 🇬🇧 English

## ✨ Features

- 🗣️ **Voice cloning** — upload or record a 5–15 s reference sample with the microphone, and the model will speak in that voice
- 📄 **Document support** — `.txt`, `.md` (markup is stripped automatically), `.docx`, `.pdf`
- 🌍 **17 languages** — Russian, English, German, Spanish, French and more
- ⚡ **GPU acceleration** — 10–20× faster than CPU on an NVIDIA GPU
- 📑 **Long texts** — documents are automatically split into chunks and joined with pauses
- 💾 **Formats** — `WAV` and `MP3`
- 🖥️ **Web UI** — everything happens in the browser, no manual steps required
- 📦 **Batch mode** — voice over a whole folder of documents with a single command

## 🚀 Quick Start

### Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) for Windows with the **WSL2** backend
- *(Optional, but highly recommended)* An **NVIDIA** GPU with up-to-date drivers
- 8+ GB of free disk space (image + model)

### Run

```powershell
docker compose up -d --build
```

Then open **http://localhost:7860** in your browser 🌐

The first run downloads the XTTS v2 model (~2 GB) and builds the image — it takes 10–20 minutes.
The model and all layers are cached, so subsequent starts take less than a minute.

```powershell
docker compose logs -f ui   # logs (you should see: 🚀 Используемое устройство: CUDA)
docker compose down         # stop
docker compose up -d        # start again (no rebuild)
```

## 🖥️ Web UI

1. **Text** — paste it into the field or upload a document: the text will be filled in automatically
2. **Voice**
   - pick a built-in voice from the dropdown, **or**
   - upload/record a 5–15 s clean reference sample — the voice will be cloned
     (the reference takes priority over built-in voices)
   - if nothing is selected, the **default voice** (a built-in male XTTS v2 voice) is used automatically
3. **Language & format** — `ru` by default, `wav` or `mp3`
4. Press **«🔊 Озвучить»** — long texts show per-chunk progress
5. Listen to and download the result right on the page

> 💡 XTTS v2's built-in voices are English and sound accented in Russian.
> Use voice cloning for a natural Russian sound.

## 📦 Batch Mode

Voice over a whole folder of documents without the web UI:

1. Put your documents into `input\`
2. *(Optional)* Put a 5–15 s voice sample into `reference\male_voice.wav`
3. Run:

```powershell
docker compose --profile batch run --rm batch
```

The generated files will appear in `output\`.

## 🗂️ Project Structure

```text
ozvuchka/
├── Dockerfile                 # image: python:3.10-slim + ffmpeg + CUDA PyTorch
├── docker-compose.yml         # services: ui (web) and batch (batch mode)
├── requirements.txt           # dependencies with pinned compatible versions
├── app/
│   ├── ui.py                  # Gradio web UI
│   ├── main.py                # batch mode
│   ├── tts_engine.py          # XTTS v2 engine: text chunking, joining, progress
│   ├── document_parser.py     # reads .txt / .md / .docx / .pdf
│   └── config.py              # environment-based settings
├── input/                     # 📥 documents for batch mode
├── output/                    # 📤 batch mode output
└── reference/                 # 🎭 voice reference for cloning
```

## ⚙️ Configuration

Settings are passed through environment variables in `docker-compose.yml`:

| Variable          | Value                       | Description                            |
|-------------------|-----------------------------|----------------------------------------|
| `LANGUAGE`        | `ru`                        | Default language                       |
| `REFERENCE_AUDIO` | `/reference/male_voice.wav` | Voice reference for batch mode         |
| `OUTPUT_FORMAT`   | `wav`                       | Batch mode output format (`wav`/`mp3`) |
| `SAMPLE_RATE`     | `24000`                     | XTTS v2 operates at 24 kHz             |

## 🧠 How It Works

- **Generation** — the XTTS v2 neural network generates 24 kHz speech directly on the GPU
- **Voice cloning** — the model extracts a voice embedding from the reference and reproduces its timbre in any language
- **Long texts** — text is split into chunks of up to 250 characters, each generated separately,
  then joined with short pauses at the boundaries
- **Markdown** — headings, links, code blocks and other markup are removed from `.md` files before synthesis
- **Model cache** — the model (~2 GB) lives in the `tts-models` Docker volume and is never re-downloaded

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `CPU` in the log instead of `CUDA` | GPU passthrough failed: update the NVIDIA driver and make sure Docker Desktop uses the WSL2 backend |
| No GPU — need CPU | Remove the `deploy` blocks from the `ui` and `batch` services in `docker-compose.yml` |
| Nothing selected in the voice field | Not a problem: the default voice (built-in male XTTS v2 voice) is used |
| Error `\r: command not found` | Files must use LF line endings (enforced by `.gitattributes` in this repo) |
| Check GPU inside the container | `docker compose run --rm ui python -c "import torch; print(torch.cuda.is_available())"` |

---

## 📄 Лицензия · License

Код распространяется по лицензии [MIT](LICENSE).
The code is licensed under [MIT](LICENSE).

Модель **XTTS v2** распространяется по собственной некоммерческой лицензии
[Coqui Public Model License (CPML)](https://coqui.ai/cpml.txt) — использование для
личных целей разрешено, для коммерческих проектов ознакомьтесь с условиями лицензии.
The **XTTS v2** model is distributed under its own non-commercial
[Coqui Public Model License (CPML)](https://coqui.ai/cpml.txt) — free for personal use;
please review the terms for commercial projects.

---

<div align="center">

Сделано с ❤️ для тех, кто любит, когда текст говорит.
*Made with ❤️ for those who love it when text speaks.*

</div>
