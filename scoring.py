# -*- coding: utf-8 -*-
"""Автопроверка закрытых вопросов — без ИИ, чистая математика."""
from collections import defaultdict
from config import percent_to_scale5


def score_closed(question_bank: dict, responses: dict) -> dict:
    """
    Возвращает:
      - per_competency: {competency: {"correct": n, "total": m, "percent": %, "scale5": x}}
      - total_correct, total_questions, overall_percent
    """
    q_by_id = {q["q_id"]: q for q in question_bank["closed_questions"]}
    per_comp = defaultdict(lambda: {"correct": 0, "total": 0})

    for ans in responses["closed_answers"]:
        q = q_by_id.get(ans["q_id"])
        if not q:
            continue
        comp = q["competency"]
        per_comp[comp]["total"] += 1
        if ans["chosen"] == q["correct"]:
            per_comp[comp]["correct"] += 1

    per_competency = {}
    total_correct = total_questions = 0
    for comp, v in per_comp.items():
        pct = 100.0 * v["correct"] / v["total"] if v["total"] else 0.0
        per_competency[comp] = {
            "correct": v["correct"],
            "total": v["total"],
            "percent": round(pct, 1),
            "scale5": percent_to_scale5(pct),
        }
        total_correct += v["correct"]
        total_questions += v["total"]

    overall = round(100.0 * total_correct / total_questions, 1) if total_questions else 0.0
    return {
        "per_competency": per_competency,
        "total_correct": total_correct,
        "total_questions": total_questions,
        "overall_percent": overall,
    }
