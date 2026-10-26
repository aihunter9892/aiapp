import unittest

from watch import clean, classify, render

POST = "https://www.linkedin.com/posts/someone_activity-123-abc"


class ClassifyTests(unittest.TestCase):
    def test_request_for_ai_trainer_is_kept(self):
        match = classify(
            "Priya on LinkedIn: We are looking for an AI trainer for our staff",
            "Need recommendations for a corporate AI trainer, DM me.",
            POST,
        )
        self.assertIsNotNone(match)
        self.assertEqual(match["url"], POST)

    def test_generative_ai_workshop_request_is_kept(self):
        self.assertIsNotNone(
            classify("Looking for a generative AI workshop provider", "", POST)
        )

    def test_trainer_offer_is_dropped(self):
        self.assertIsNone(
            classify(
                "I run corporate AI training",
                "I offer a generative AI workshop for teams. Book a call.",
                POST,
            )
        )

    def test_unrelated_hiring_post_is_dropped(self):
        self.assertIsNone(
            classify("We are hiring a backend engineer", "Python and Go", POST)
        )

    def test_non_linkedin_url_is_dropped(self):
        self.assertIsNone(
            classify(
                "Looking for an AI trainer",
                "",
                "https://example.com/looking-for-ai-trainer",
            )
        )

    def test_linkedin_profile_page_is_dropped(self):
        self.assertIsNone(
            classify(
                "Looking for an AI trainer",
                "",
                "https://www.linkedin.com/in/someone",
            )
        )


class HelperTests(unittest.TestCase):
    def test_clean_removes_highlight_tags(self):
        self.assertEqual(clean("<strong>AI</strong> trainer &amp; coach"), "AI trainer & coach")

    def test_render_empty_day(self):
        self.assertIn("No new requests found.", render([], "2026-10-26"))

    def test_render_lists_match(self):
        text = render([{"title": "T", "url": POST, "snippet": "S"}], "2026-10-26")
        self.assertIn(POST, text)


if __name__ == "__main__":
    unittest.main()
