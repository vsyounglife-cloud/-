# -*- coding: utf-8 -*-
"""
Главный скрипт: ответы сотрудника -> цифровой профиль (PDF).

Запуск:
    python run_pipeline.py data/responses_sample.json

Сборка отчёта проходит через 4 этапа:
    1) Автопроверка закрытых вопросов (без ИИ)
    2) AI-анализ открытых кейсов (mock / ollama / gemini — см. config.py)
    3) Расчёт компетенций и общего вердикта
    4) Генерация PDF по фирменному шаблону
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from report_builder import build_profile      # noqa: E402
from generate_pdf import render_pdf           # noqa: E402

BASE = os.path.dirname(__file__)
QUESTION_BANK = os.path.join(BASE, "data", "question_bank.json")
OUTPUT_DIR = os.path.join(BASE, "output")


def main():
    responses_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "data", "responses_sample.json")

    with open(QUESTION_BANK, encoding="utf-8") as f:
        question_bank = json.load(f)
    with open(responses_path, encoding="utf-8") as f:
        responses = json.load(f)

    print("1-3) Сборка профиля (подсчёт + AI-анализ кейсов)...")
    profile = build_profile(question_bank, responses)

    # Сохраняем промежуточный JSON (удобно для дашбордов / Power BI)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_name = profile["employee"]["name"].replace(" ", "_")
    json_path = os.path.join(OUTPUT_DIR, f"profile_{safe_name}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    print("4) Генерация PDF...")
    pdf_path = os.path.join(OUTPUT_DIR, f"Отчет_{safe_name}.pdf")
    render_pdf(profile, pdf_path)

    print(f"\nГотово!")
    print(f"  Вердикт      : {profile['verdict_title']} ({profile['overall_percent']}%)")
    print(f"  JSON профиль : {json_path}")
    print(f"  PDF отчёт    : {pdf_path}")


if __name__ == "__main__":
    main()
