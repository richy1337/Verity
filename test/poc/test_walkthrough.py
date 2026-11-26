import unittest

from src.poc.walkthrough import result_lines


class WalkthroughDisplayTests(unittest.TestCase):
    def setUp(self):
        self.response = {
            "status": "completed",
            "summary_label": "The model flagged a visual pattern",
            "false_positive_warning": "Authentic images can also trigger this signal.",
            "uncertainty": "The visual model has limited evidence.",
            "signals": [
                {
                    "source": "observed_signal",
                    "locator": "JPEG metadata",
                    "summary": "Provenance metadata is absent or stripped.",
                },
                {
                    "source": "inference",
                    "locator": "Image classifier",
                    "summary": "The classifier found weak visual signals.",
                },
            ],
            "limitations": ["Re-encoding can affect visual signals."],
            "verification_steps": ["Compare this copy with the source archive."],
        }

    def test_separates_provenance_observation_from_model_inference(self):
        result = "\n".join(result_lines(self.response))
        self.assertIn("[Observed Input Signal] Provenance metadata is absent", result)
        self.assertIn(
            "[Model Inference] The classifier found weak visual signals.", result
        )
        self.assertIn(self.response["uncertainty"], result)
        self.assertIn(self.response["verification_steps"][0], result)

    def test_completed_displays_false_positive_warning_when_present(self):
        result = "\n".join(result_lines(self.response))
        self.assertIn(self.response["false_positive_warning"], result)

    def test_inconclusive_has_uncertainty_without_directional_summary(self):
        self.response["status"] = "inconclusive"
        result = "\n".join(result_lines(self.response))
        self.assertIn("Status  inconclusive", result)
        self.assertIn(self.response["uncertainty"], result)
        self.assertNotIn(self.response["summary_label"], result)
        self.assertNotIn(self.response["false_positive_warning"], result)

    def test_nonassessment_statuses_ignore_partial_result_fields(self):
        for status in ("pending", "failed", "cancelled"):
            with self.subTest(status=status):
                self.response["status"] = status
                result = "\n".join(result_lines(self.response))
                self.assertIn(f"Status  {status}", result)
                self.assertNotIn(self.response["summary_label"], result)
                self.assertNotIn("Evidence", result)

    def test_completed_result_requires_evidence(self):
        self.response["signals"] = []
        with self.assertRaisesRegex(ValueError, "required evidence"):
            result_lines(self.response)


if __name__ == "__main__":
    unittest.main()
