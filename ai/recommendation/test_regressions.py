import unittest

from adapters import adapt_student_profile, adapt_p4_program
from engine import recommend
from scoring import calculate_score


class TestRegressions(unittest.TestCase):
    def test_private_preference_alone_does_not_dominate(self):
        student = {
            "interests": ["informatique"],
            "skills": ["programmation"],
            "preferred_type": "prive",
        }
        programs = [
            {"name": "Orthophonie fictive", "type": "prive"},
            {
                "name": "Informatique fictive",
                "type": "public",
                "interests": ["informatique"],
                "skills": ["programmation"],
            },
        ]

        results = recommend(student, programs)

        self.assertEqual(results[0]["program"], "Informatique fictive")
        self.assertEqual(results[0]["score"], 50.0)
        self.assertEqual(results[1]["score"], 10.0)

    def test_missing_data_does_not_invent_a_score(self):
        self.assertIsNone(calculate_score({}, {}))

    def test_bac_code_and_zero_values_are_preserved(self):
        student = adapt_student_profile({
            "bac": "Sciences mathématiques A",
            "code_bac": "sciences_mathematiques_a",
            "notes": {"mathematiques": 0.0},
            "budget_annuel_max": 0.0,
        })

        self.assertEqual(student["bac_type"], "sciences_mathematiques_a")
        self.assertEqual(student["bac_text"], "Sciences mathématiques A")
        self.assertEqual(student["grades"]["mathematiques"], 0.0)
        self.assertEqual(student["max_annual_budget"], 0.0)

    def test_ambiguous_bac_remains_unknown(self):
        student = adapt_student_profile({
            "bac": "Sciences mathématiques",
        })

        self.assertIsNone(student["bac_type"])

    def test_uncertain_city_is_kept_with_warning(self):
        program = adapt_p4_program(
            {
                "program_id": "test-program",
                "institution_id": "test-institution",
                "name": "Formation fictive",
            },
            {
                "institution_id": "test-institution",
                "city": "Rabat",
                "city_status": "source",
                "entity_type": "etablissement",
                "sector": "public",
            },
        )

        results = recommend(
            {"preferred_city": "Rabat", "can_relocate": False},
            [program],
        )

        self.assertIsNone(program["city"])
        self.assertEqual(len(results), 1)
        self.assertIn(
            "Localisation à vérifier.",
            results[0]["constraints"]["reasons"],
        )

    def test_known_other_city_is_excluded(self):
        results = recommend(
            {"preferred_city": "Rabat", "can_relocate": False},
            [{"name": "Formation fictive", "city": "Marrakech"}],
        )

        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()