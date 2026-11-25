"""Unit tests for FileClassifier and CustomRulesManager."""

import unittest

from core.classifier import FileClassifier
from core.custom_rules import CustomRulesManager


class TestClassifier(unittest.TestCase):
    def test_case_insensitive_and_unknown_extensions(self) -> None:
        clf = FileClassifier()
        cat_img, known_img = clf.classify_extension(".JPG")
        self.assertEqual(cat_img, "Images")
        self.assertTrue(known_img)

        cat_prog, known_prog = clf.classify_extension("py")
        self.assertEqual(cat_prog, "Programming")
        self.assertTrue(known_prog)

        cat_unk, known_unk = clf.classify_extension(".xyz123")
        self.assertEqual(cat_unk, "Others")
        self.assertFalse(known_unk)

    def test_custom_rules_and_folder_rename(self) -> None:
        rules = CustomRulesManager()
        ok, _ = rules.create_custom_category("Design", [".psd", ".ai"])
        self.assertTrue(ok)
        ok_ren, _ = rules.rename_category_folder("Design", "Design_Assets")
        self.assertTrue(ok_ren)

        clf = FileClassifier(
            custom_categories=rules.settings["custom_categories"],
            category_folder_names=rules.settings["category_folder_names"],
        )
        cat, known = clf.classify_extension(".PSD")
        self.assertEqual(cat, "Design")
        self.assertTrue(known)
        self.assertEqual(clf.get_folder_name("Design"), "Design_Assets")


if __name__ == "__main__":
    unittest.main()
