import os
from pathlib import Path

from dotenv import load_dotenv

# В sandbox у CrewAI может не быть прав писать в AppData, поэтому
# перенаправляем служебное хранилище в локальную папку проекта.
os.environ.setdefault("CREWAI_STORAGE_DIR", str(Path(".crewai").resolve()))

from crewai import Agent, Crew, Process, Task


def configure_openai_base_url() -> None:
    """Настраивает OpenAI-совместимый base URL (например, ProxyAPI)."""
    proxy_base_url = os.getenv("PROXYAPI_BASE_URL", "").strip()
    if proxy_base_url:
        # LiteLLM/CrewAI могут читать один из этих env-параметров.
        os.environ["OPENAI_BASE_URL"] = proxy_base_url
        os.environ["OPENAI_API_BASE"] = proxy_base_url


def resolve_model_name() -> str:
    """Возвращает имя модели для LLM, игнорируя URL базы данных."""
    database_url = os.getenv("DATABASE_URL", "").strip().lower()

    # Если в DATABASE_URL лежит URL БД (sqlite/postgres/mysql), это не модель.
    if database_url.startswith(("sqlite:", "postgres:", "postgresql:", "mysql:")):
        return os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini").strip()

    # Если пользователь по-прежнему хранит модель в DATABASE_URL, поддержим fallback.
    return os.getenv("DATABASE_URL", "").strip() or os.getenv(
        "OPENAI_MODEL_NAME", "gpt-4o-mini"
    ).strip()


def validate_file(path_str: str) -> Path:
    """Проверяет, что файл существует, имеет .txt и не пустой."""
    file_path = Path(path_str.strip())

    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError("Файл не найден.")

    if file_path.suffix.lower() != ".txt":
        raise ValueError("Неверный формат файла. Нужен .txt файл.")

    if file_path.stat().st_size == 0:
        raise ValueError("Файл пустой.")

    return file_path


def read_text(file_path: Path) -> str:
    """Читает текст из файла и проверяет, что после strip он не пустой."""
    try:
        content = file_path.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        # Простой fallback, если файл не в UTF-8
        content = file_path.read_text(encoding="cp1251").strip()
    except OSError as exc:
        raise OSError(f"Ошибка чтения файла: {exc}") from exc

    if not content:
        raise ValueError("Файл содержит только пустые строки/пробелы.")

    return content


def create_agents() -> tuple[Agent, Agent, Agent]:
    """Создает 3 простых агента CrewAI."""
    model_name = resolve_model_name()

    main_idea_agent = Agent(
        role="Аналитик главной мысли",
        goal="Определить главную мысль текста",
        backstory="Ты кратко и ясно выделяешь основной смысл текста.",
        verbose=False,
        allow_delegation=False,
        llm=model_name,
    )

    summary_agent = Agent(
        role="Краткий резюмер",
        goal="Сделать краткое резюме текста",
        backstory="Ты делаешь лаконичное резюме на 3-5 предложений.",
        verbose=False,
        allow_delegation=False,
        llm=model_name,
    )

    actions_agent = Agent(
        role="Советник по действиям",
        goal="Предложить 3 простых следующих действия",
        backstory="Ты предлагаешь понятные и практичные шаги.",
        verbose=False,
        allow_delegation=False,
        llm=model_name,
    )

    return main_idea_agent, summary_agent, actions_agent


def run_crew(text: str) -> str:
    """Создает задачи и запускает Crew в последовательном режиме."""
    main_idea_agent, summary_agent, actions_agent = create_agents()

    task_1 = Task(
        description=(
            "Прочитай текст и определи его главную мысль в 1-2 предложениях.\n\n"
            f"Текст:\n{text}"
        ),
        expected_output="1-2 предложения с главной мыслью.",
        agent=main_idea_agent,
    )

    task_2 = Task(
        description=(
            "Сделай краткое резюме текста на 3-5 предложений.\n\n"
            f"Текст:\n{text}"
        ),
        expected_output="Резюме на 3-5 предложений.",
        agent=summary_agent,
    )

    task_3 = Task(
        description=(
            "Предложи 3 простых следующих действия на основе текста. "
            "Оформи в виде списка из 3 пунктов.\n\n"
            f"Текст:\n{text}"
        ),
        expected_output="Список из 3 простых действий.",
        agent=actions_agent,
    )

    crew = Crew(
        agents=[main_idea_agent, summary_agent, actions_agent],
        tasks=[task_1, task_2, task_3],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()
    return str(result).strip()


def main() -> None:
    """Точка входа: запрашивает путь, валидирует файл, запускает анализ."""
    load_dotenv()
    configure_openai_base_url()

    print("=== Простой анализ текста через CrewAI ===")
    file_input = input("Введите путь к txt-файлу: ").strip()

    try:
        valid_path = validate_file(file_input)
        text = read_text(valid_path)
        final_result = run_crew(text)
    except FileNotFoundError as exc:
        print(f"Ошибка: {exc}")
        return
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return
    except OSError as exc:
        print(f"Ошибка: {exc}")
        return
    except Exception as exc:
        print(f"Непредвиденная ошибка: {exc}")
        return

    print("\n=== Результат анализа ===")
    print(final_result)


if __name__ == "__main__":
    main()
