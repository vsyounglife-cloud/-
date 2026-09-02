# -*- coding: utf-8 -*-
"""Собирает единый профиль сотрудника: числа + AI-оценки кейсов + вердикт."""
from config import (COMPETENCIES, status_for_score, verdict_for_percent,
                    percent_to_scale5)
from scoring import score_closed
from ai_analyzer import analyze_case


VERDICT_SUMMARY = {
    "ВЫДАЮЩИЙСЯ ДИРЕКТОР": "Эталонный управленец с системным мышлением. Стабильно превышает цели, развивает команду и выстраивает автономные процессы даже в пиковые периоды.",
    "ЭФФЕКТИВНЫЙ ДИРЕКТОР": "Сильный управленец, полностью адаптированный к современным реалиям розницы. Уверенно балансирует между финансовыми целями, качеством сервиса и операционной дисциплиной, формируя вовлечённую и продуктивную команду.",
    "РАЗВИВАЮЩИЙСЯ ДИРЕКТОР": "Уверенно закрывает базовые задачи филиала. Есть чёткие зоны роста в аналитике и развитии команды, проработка которых выведет магазин на новый уровень эффективности.",
    "ТРЕБУЕТ РАЗВИТИЯ": "Демонстрирует базовое понимание роли. Необходим индивидуальный план развития по ключевым компетенциям и наставническая поддержка.",
}


def build_profile(question_bank: dict, responses: dict) -> dict:
    # 1. Закрытые вопросы
    closed = score_closed(question_bank, responses)

    # 2. AI-анализ открытых кейсов
    cases_by_id = {c["case_id"]: c for c in question_bank["open_cases"]}
    case_scores = {}   # competency -> [scores]
    case_analyses = {} # competency -> analysis text
    for ans in responses.get("open_answers", []):
        case = cases_by_id.get(ans["case_id"])
        if not case:
            continue
        comp = case["competency"]
        comp_name = COMPETENCIES[comp]["name_ru"]
        result = analyze_case(case, comp_name, ans["text"])
        case_scores.setdefault(comp, []).append(result["score"])
        case_analyses[comp] = result["analysis"]

    # 3. Итоговый балл по каждой компетенции (среднее закрытых и кейсов)
    competencies = []
    for comp_key, comp_meta in COMPETENCIES.items():
        parts = []
        closed_c = closed["per_competency"].get(comp_key)
        if closed_c:
            parts.append(closed_c["scale5"])
        if comp_key in case_scores:
            parts.extend(case_scores[comp_key])
        if not parts:
            continue
        score5 = round(sum(parts) / len(parts), 1)
        analysis = case_analyses.get(
            comp_key,
            f"Показатель уверенно закрыт по итогам теоретической части. "
            f"Сотрудник демонстрирует стабильное владение компетенцией."
        )
        competencies.append({
            "name_ru": comp_meta["name_ru"],
            "name_kz": comp_meta["name_kz"],
            "score5": score5,
            "percent5": round(score5 / 5.0 * 100, 1),
            "status": status_for_score(score5),
            "analysis": analysis,
        })

    # 4. Общий вердикт
    overall = closed["overall_percent"]
    verdict_title = verdict_for_percent(overall)

    return {
        "employee": responses["employee"],
        "campaign": question_bank["campaign"],
        "meta": responses["meta"],
        "overall_percent": overall,
        "total_correct": closed["total_correct"],
        "total_questions": closed["total_questions"],
        "verdict_title": verdict_title,
        "verdict_summary": VERDICT_SUMMARY.get(verdict_title, ""),
        "competencies": competencies,
    }
