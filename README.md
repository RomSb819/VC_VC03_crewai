# Simple CrewAI Text Analyzer

Минимальная консольная программа на Python + CrewAI.

Программа:
- запрашивает путь к `.txt` файлу;
- проверяет файл (существует, `.txt`, не пустой);
- читает текст;
- запускает 3 агента CrewAI:
  - главная мысль;
  - резюме (3-5 предложений);
  - 3 следующих действия;
- выводит результат в консоль.

## 1) Установка зависимостей

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) Подготовка ключа модели

CrewAI использует LLM, поэтому нужен API-ключ.
Если вы используете ProxyAPI, укажите OpenAI-совместимый `base_url`.

Создайте файл `.env` рядом с `main.py`:

```env
OPENAI_API_KEY=ваш_ключ_proxyapi
OPENAI_MODEL_NAME=gpt-4o
PROXYAPI_BASE_URL=https://api.proxyapi.ru/openai/v1
DATABASE_URL=sqlite:///instance/app.db
```

Важно:
- `OPENAI_MODEL_NAME` это имя LLM-модели.
- `DATABASE_URL` это адрес базы данных (если нужен в будущем) и не должен быть именем модели.
- `PROXYAPI_BASE_URL` используется как `base_url` для OpenAI-совместимого API.

## 3) Запуск программы

```bash
python main.py
```

## 4) Пример использования

```text
=== Простой анализ текста через CrewAI ===
Введите путь к txt-файлу: sample.txt

=== Результат анализа ===
(вывод CrewAI: главная мысль, краткое резюме и 3 действия)
```

## Структура проекта

- `main.py`
- `requirements.txt`
- `README.md`
