"""Transparent, explainable symptom-to-condition scoring.

Rather than a black-box classifier, we score each candidate ``Condition``
by how much of its known symptom set the patient reported (recall) and
how much of what the patient reported matches that condition (precision),
then combine them into a single confidence percentage. This keeps the
whole pipeline explainable in an interview or code review.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Condition, Symptom


@dataclass
class TriageResult:
    condition: Condition | None
    confidence: float
    matched_symptoms: list[str]
    alternatives: list[tuple[Condition, float]]


def assess_symptoms(symptom_ids: list[int]) -> TriageResult:
    reported = set(Symptom.objects.filter(pk__in=symptom_ids))
    if not reported:
        return TriageResult(None, 0.0, [], [])

    scored: list[tuple[Condition, float, set[Symptom]]] = []
    for condition in Condition.objects.prefetch_related("symptoms").all():
        condition_symptoms = set(condition.symptoms.all())
        if not condition_symptoms:
            continue
        overlap = reported & condition_symptoms
        if not overlap:
            continue
        recall = len(overlap) / len(condition_symptoms)  # how much of the condition is covered
        precision = len(overlap) / len(reported)  # how much of the input is explained
        confidence = round(((recall + precision) / 2) * 100, 1)
        scored.append((condition, confidence, overlap))

    if not scored:
        return TriageResult(None, 0.0, [], [])

    scored.sort(key=lambda item: item[1], reverse=True)
    top_condition, top_confidence, top_overlap = scored[0]
    alternatives = [(c, conf) for c, conf, _ in scored[1:4]]

    return TriageResult(
        condition=top_condition if top_confidence >= 25 else None,
        confidence=top_confidence,
        matched_symptoms=[s.name for s in top_overlap],
        alternatives=alternatives,
    )
