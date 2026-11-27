from django.test import TestCase

from apps.triage.models import Condition, Symptom
from apps.triage.services import assess_symptoms


class TriageScoringTests(TestCase):
    def setUp(self):
        self.fever = Symptom.objects.create(name="fever")
        self.cough = Symptom.objects.create(name="cough")
        self.rash = Symptom.objects.create(name="skin_rash")

        self.flu = Condition.objects.create(name="Influenza", severity=Condition.Severity.MODERATE)
        self.flu.symptoms.set([self.fever, self.cough])

        self.allergy = Condition.objects.create(name="Allergic Reaction", severity=Condition.Severity.LOW)
        self.allergy.symptoms.set([self.rash])

    def test_matching_symptoms_returns_best_condition(self):
        result = assess_symptoms([self.fever.pk, self.cough.pk])
        self.assertEqual(result.condition, self.flu)
        self.assertGreater(result.confidence, 0)

    def test_no_symptoms_returns_empty_result(self):
        result = assess_symptoms([])
        self.assertIsNone(result.condition)
        self.assertEqual(result.confidence, 0.0)

    def test_unrelated_symptom_does_not_match(self):
        unrelated = Symptom.objects.create(name="dizziness")
        result = assess_symptoms([unrelated.pk])
        self.assertIsNone(result.condition)
