import json
import unittest

from engine import recommend


class TestEngine(unittest.TestCase):

    def setUp(self):
        self.student = {
            "interests": ["informatique"],
            "grades": {"maths": 16},
            "skills": ["programmation"],
            "career_goal": "ingenieur",
            "preferred_type": "public"
        }

        self.programs = [
            {
                "name": "Formation moins compatible",
                "interests": ["commerce"],
                "required_subjects": ["economie"],
                "skills": ["negociation"],
                "career_paths": ["commercial"],
                "type": "prive"
            },
            {
                "name": "Formation informatique",
                "interests": ["informatique"],
                "required_subjects": ["maths"],
                "skills": ["programmation"],
                "career_paths": ["ingenieur"],
                "type": "public"
            }
        ]

    def test_ranking_score_and_explanations(self):
        results = recommend(self.student, self.programs)

        self.assertEqual(len(results), 2)
        self.assertEqual(
            results[0]["program"],
            "Formation informatique"
        )
        self.assertEqual(results[0]["score"], 95.0)
        self.assertEqual(results[1]["score"], 0.0)
        self.assertEqual(len(results[0]["explanations"]), 5)

    def test_top_n(self):
        results = recommend(self.student, self.programs, top_n=1)
        self.assertEqual(len(results), 1)

    def test_empty_programs(self):
        self.assertEqual(recommend(self.student, []), [])

    def test_invalid_top_n(self):
        for value in [0, -1]:
            with self.assertRaises(ValueError):
                recommend(self.student, self.programs, top_n=value)

        for value in [True, 1.5, "5"]:
            with self.assertRaises(TypeError):
                recommend(self.student, self.programs, top_n=value)

    def test_json_serialization(self):
        results = recommend(self.student, self.programs)
        serialized = json.dumps(results, ensure_ascii=False)
        self.assertEqual(json.loads(serialized), results)

    def test_excludes_ineligible_program(self):
        student = {
            **self.student,
            "bac_type": "sciences_maths"
        }
        program = {
            **self.programs[1],
            "accepted_bac_types": ["lettres"]
        }

        self.assertEqual(recommend(student, [program]), [])

    def test_excludes_over_budget_program(self):
        student = {
            **self.student,
            "max_annual_budget": 10000
        }
        program = {
            **self.programs[1],
            "annual_cost": 20000
        }

        self.assertEqual(recommend(student, [program]), [])

    def test_excludes_program_when_relocation_impossible(self):
        student = {
            **self.student,
            "preferred_city": "Marrakech",
            "can_relocate": False
        }
        program = {
            **self.programs[1],
            "city": "Rabat"
        }

        self.assertEqual(recommend(student, [program]), [])

    def test_keeps_unknown_constraints_with_reasons(self):
        results = recommend(self.student, [self.programs[1]])

        self.assertEqual(len(results), 1)
        constraints = results[0]["constraints"]
        self.assertEqual(constraints["eligibility"], "unknown")
        self.assertEqual(constraints["feasibility"], "unknown")
        self.assertTrue(constraints["reasons"])
        
if __name__ == "__main__":
    unittest.main()