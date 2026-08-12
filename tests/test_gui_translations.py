import unittest

from gui import TRANSLATIONS, tr


class TranslationTests(unittest.TestCase):
    def test_languages_have_the_same_keys(self):
        self.assertEqual(set(TRANSLATIONS["en"]), set(TRANSLATIONS["he"]))

    def test_every_translation_can_be_formatted(self):
        values = {"path": "C:\\Test", "error": "test", "count": 2}
        for language, translations in TRANSLATIONS.items():
            for key in translations:
                with self.subTest(language=language, key=key):
                    self.assertIsInstance(tr(language, key, **values), str)

    def test_language_button_names_the_other_language(self):
        self.assertNotEqual(tr("en", "language"), tr("he", "language"))


if __name__ == "__main__":
    unittest.main()
