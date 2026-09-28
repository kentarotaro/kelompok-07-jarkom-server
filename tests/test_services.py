import unittest
from unittest import result
from core.services import SERVICE_REGISTRY
from core.fault_injector import FaultInjector

class TestService(unittest.TestCase):
    def test_char_count(self):
        result = SERVICE_REGISTRY["CHAR_COUNT"]("Hello World")
        self.assertEqual(result, 11)

    def test_word_count(self):
        result = SERVICE_REGISTRY["WORD_COUNT"]("Hello World")
        self.assertEqual(result, 2)

    def test_reverse_string(self):
        result = SERVICE_REGISTRY["REVERSE_STRING"]("Hello")
        self.assertEqual(result, "olleH")

    def test_remove_vowels(self):
        result = SERVICE_REGISTRY["REMOVE_VOWELS"]("Ilmu komputer")
        self.assertEqual(result, "lm kmptr")

    def test_matrix_3x3(self):
        matrix = [
            [1, 2, 3],
            [0, 1, 4],
            [5, 6, 0]
        ]
        result = SERVICE_REGISTRY["MATRIX_3X3"](matrix)
        self.assertEqual(result["determinant"], 1.0)
        self.assertEqual(result["inverse"], [[-24.0, 18.0, 5.0], [20.0, -15.0, -4.0], [-5.0, 4.0, 1.0]])

    def test_fault_injector_force(self):
        # test jika dipaksa salah dengan ate 100%
        corrupted = FaultInjector.apply("CHAR_COUNT", 10, rate=1.0)
        self.assertNotEqual(corrupted, 10)

        # tes jika terdapat palindrom pada reverse string
        corrupted_reverse = FaultInjector.apply("REVERSE_STRING", "malam", rate=1.0)
        self.assertNotEqual(corrupted_reverse, "malam")

if __name__ == "__main__":
    unittest.main()