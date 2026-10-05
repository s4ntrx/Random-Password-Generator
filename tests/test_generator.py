import string
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passgen import Options, entropy_bits, generate_password, strength_label
from passgen.generator import AMBIGUOUS_CHARS, MAX_LENGTH, MIN_LENGTH


class GeneratePasswordTests(unittest.TestCase):
    def test_length_is_respected(self):
        for length in (MIN_LENGTH, 16, 64, MAX_LENGTH):
            self.assertEqual(len(generate_password(Options(length=length))), length)

    def test_every_enabled_set_is_present(self):
        for _ in range(200):
            password = generate_password(Options(length=MIN_LENGTH))
            self.assertTrue(any(c in string.ascii_lowercase for c in password))
            self.assertTrue(any(c in string.ascii_uppercase for c in password))
            self.assertTrue(any(c in string.digits for c in password))
            self.assertTrue(any(c in string.punctuation for c in password))

    def test_disabled_sets_are_absent(self):
        password = generate_password(Options(length=64, symbols=False, digits=False))
        self.assertTrue(password.isalpha())

    def test_ambiguous_characters_are_excluded(self):
        for _ in range(200):
            password = generate_password(Options(length=64, exclude_ambiguous=True))
            self.assertFalse(AMBIGUOUS_CHARS & set(password))

    def test_invalid_options_raise(self):
        with self.assertRaises(ValueError):
            generate_password(Options(lowercase=False, uppercase=False, digits=False, symbols=False))
        with self.assertRaises(ValueError):
            generate_password(Options(length=MIN_LENGTH - 1))
        with self.assertRaises(ValueError):
            generate_password(Options(length=MAX_LENGTH + 1))

    def test_passwords_differ(self):
        self.assertEqual(len({generate_password() for _ in range(100)}), 100)


class StrengthTests(unittest.TestCase):
    def test_entropy_grows_with_length(self):
        self.assertGreater(entropy_bits(Options(length=20)), entropy_bits(Options(length=10)))

    def test_labels(self):
        self.assertEqual(strength_label(10), "Weak")
        self.assertEqual(strength_label(50), "Fair")
        self.assertEqual(strength_label(70), "Strong")
        self.assertEqual(strength_label(120), "Very strong")


if __name__ == "__main__":
    unittest.main()
