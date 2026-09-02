# Nisaba Assessment Platform — MVP

Бесплатная платформа тестирования, которая по ответам сотрудника генерирует
«Цифровой профиль сотрудника» в PDF — с общим баллом, вердиктом и детализацией
по компетенциям (включая AI-анализ открытых кейсов).

## Что внутри

```
assessment-platform/
├── run_pipeline.py            # главный скрипт запуска
├── data/
│   ├── question_bank.json     # банк вопросов: закрытые + кейсы, с тегами компетенций
│   └── responses_sample.json  # пример ответов сотрудника (как из Forms)
├── src/
│   ├── config.py              # компетенции, шкалы, статусы, вердикты, AI-настройки
│   ├── scoring.py             # автопроверка закрытых вопросов (без ИИ)
│   ├── ai_analyzer.py         # AI-анализ кейсов (mock / ollama / gemini)
│   ├── report_builder.py      # сборка единого профиля
│   └── generate_pdf.py        # HTML-шаблон -> PDF
├── templates/
│   └── report_template.html   # фирменный дизайн отчёта (полосы прогресса, вердикт)
└── output/                    # готовые PDF и JSON-профили
```

## Запуск (3 команды)

```bash
pip install jinja2 weasyprint          # разово
cd assessment-platform
python run_pipeline.py                  # соберёт PDF из responses_sample.json
```

Готовый отчёт появится в `output/Отчет_<ФИО>.pdf`.
Для своего сотрудника: `python run_pipeline.py data/мой_сотрудник.json`

## Как это устроено (4 этапа)

1. **Автопроверка закрытых вопросов** — чистая математика, ИИ не тратится.
   `% верных → шкала /5` по каждой компетенции.
2. **AI-анализ открытых кейсов** — 1 вызов модели на кейс: возвращает балл + текст.
3. **Сборка компетенций и вердикта** — среднее по закрытым и кейсам, статус по правилу.
4. **Генерация PDF** — Jinja2 + WeasyPrint по фирменному шаблону.

## Переключение AI-провайдера (в `src/config.py`)

| provider | Стоимость | Когда использовать |
|----------|-----------|--------------------|
| `mock`   | 0 (офлайн)| Демо/отладка без сети |
| `ollama` | 0 (локально) | **Прод**: приватно, данные не покидают компанию |
| `gemini` | free tier | Быстрый старт без своего сервера |

**Ollama (рекомендуется):**
```bash
# 1. установить ollama (ollama.com), затем:
ollama pull qwen2.5:7b
# 2. в config.py: AI_CONFIG["provider"] = "ollama"
```

**Gemini free:**
```bash
export GEMINI_API_KEY="ваш_ключ"
# в config.py: AI_CONFIG["provider"] = "gemini"
```

## Интеграция со сбором ответов

Форма (Microsoft Forms / Google Forms) → выгрузка в таблицу → скрипт-конвертер
приводит строку таблицы к формату `responses_sample.json`. Каждый вопрос в
`question_bank.json` помечен `competency` — это обязательно для расчёта 6 компетенций.

## Что даёт JSON-профиль

Кроме PDF pipeline сохраняет `output/profile_<ФИО>.json` — его удобно грузить
пачкой в **Power BI / Excel** для сводных дашбордов по всем сотрудникам.

## Настройка под себя

- **Компетенции и двуязычные названия** → `src/config.py` → `COMPETENCIES`
- **Границы статусов и вердиктов** → `STATUS_RULES`, `VERDICT_RULES`
- **Дизайн отчёта** (цвета, логотип) → `templates/report_template.html`
- **Промпт ассессора** → `src/ai_analyzer.py` → `PROMPT_TEMPLATE`
