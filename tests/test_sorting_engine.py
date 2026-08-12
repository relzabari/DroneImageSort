import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sorting_engine import classify_filename, sort_drone_images


class ClassificationTests(unittest.TestCase):
    def test_classifies_supported_suffixes_case_insensitively(self):
        cases = {
            "flight_T.JPG": "Thermal",
            "flight_w.jpg": "Wide",
            "flight_V.JPG": "Visual",
            "flight_z.jpg": "Visual",
            "ordinary.jpg": "Other",
            "notes.txt": "Other",
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(classify_filename(filename), expected)


class SortingTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source"
        self.source.mkdir()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_source(self, name, content=b"content"):
        path = self.source / name
        path.write_bytes(content)
        return path

    def test_creates_only_categories_that_are_used(self):
        self.write_source("thermal_t.jpg")
        destination = self.root / "new-destination"

        result = sort_drone_images(str(self.source), str(destination))

        self.assertTrue(result.success)
        self.assertTrue((destination / "Thermal" / "thermal_t.jpg").exists())
        for unused in ("Visual", "Wide", "Other"):
            self.assertFalse((destination / unused).exists())

    def test_sorts_in_place_when_destination_is_omitted(self):
        self.write_source("wide_w.jpg")

        result = sort_drone_images(str(self.source))

        self.assertTrue(result.success)
        self.assertEqual(result.destination_folder, str(self.source))
        self.assertTrue((self.source / "Wide" / "wide_w.jpg").exists())

    def test_skips_only_identical_file(self):
        source_file = self.write_source("same_t.jpg", b"same")
        destination = self.root / "destination"
        (destination / "Thermal").mkdir(parents=True)
        (destination / "Thermal" / "same_t.jpg").write_bytes(b"same")

        result = sort_drone_images(str(self.source), str(destination))

        self.assertTrue(result.success)
        self.assertEqual(result.identical_skipped, 1)
        self.assertEqual(result.skipped, 1)
        self.assertTrue(source_file.exists())

    def test_renames_different_conflicts_with_next_available_suffix(self):
        self.write_source("photo_v.jpg", b"new")
        destination = self.root / "destination"
        visual = destination / "Visual"
        visual.mkdir(parents=True)
        (visual / "photo_v.jpg").write_bytes(b"old")
        (visual / "photo_v_2.jpg").write_bytes(b"also old")

        result = sort_drone_images(str(self.source), str(destination))

        self.assertTrue(result.success)
        self.assertEqual(result.renamed, 1)
        self.assertEqual((visual / "photo_v_3.jpg").read_bytes(), b"new")

    def test_moves_unrecognized_files_to_other(self):
        self.write_source("notes.txt")

        result = sort_drone_images(str(self.source))

        self.assertEqual(result.moved_to_other, 1)
        self.assertTrue((self.source / "Other" / "notes.txt").exists())

    def test_reports_missing_source(self):
        missing = self.root / "missing"

        result = sort_drone_images(str(missing))

        self.assertFalse(result.success)
        self.assertEqual(len(result.errors), 1)
        self.assertIn("does not exist", result.errors[0])

    def test_reports_move_errors(self):
        self.write_source("locked_t.jpg")

        with patch("sorting_engine.shutil.move", side_effect=PermissionError("locked")):
            result = sort_drone_images(str(self.source))

        self.assertFalse(result.success)
        self.assertEqual(result.skipped, 1)
        self.assertIn("locked", result.errors[0])

    def test_progress_callback_receives_operations(self):
        self.write_source("image_z.jpg")
        events = []

        result = sort_drone_images(
            str(self.source), progress=lambda level, message: events.append((level, message))
        )

        self.assertTrue(result.success)
        self.assertTrue(any("Moved to Visual" in message for _, message in events))


if __name__ == "__main__":
    unittest.main()
