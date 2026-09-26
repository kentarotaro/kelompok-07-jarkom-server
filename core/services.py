from typing import Dict, Any, List, Optional

def char_count(text: str) -> int:
    """Mengembalikan jumlah karakter dari string (termasuk spasi)."""
    return len(text)


def word_count(text: str) -> int:
    """Mengembalikan jumlah kata dari string."""
    return len(text.split())


def reverse_string(text: str) -> str:
    """Mengembalikan string yang dibalik urutannya."""
    return text[::-1]


def remove_vowels(text: str) -> str:
    """Mengembalikan string tanpa huruf vokal (a, i, u, e, o), case-insensitive."""
    vowels = "aeiouAEIOU"
    return "".join([char for char in text if char not in vowels])


def matrix_3x3(matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Menghitung nilai determinan dan invers dari matriks 3x3.
    Input format: List of 3 lists, masing-masing berisi 3 angka.
    """
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("Input harus berupa matriks 3x3")

    m00, m01, m02 = matrix[0][0], matrix[0][1], matrix[0][2]
    m10, m11, m12 = matrix[1][0], matrix[1][1], matrix[1][2]
    m20, m21, m22 = matrix[2][0], matrix[2][1], matrix[2][2]

    det = (
        m00 * (m11 * m22 - m12 * m21) -
        m01 * (m10 * m22 - m12 * m20) +
        m02 * (m10 * m21 - m11 * m20)
    )

    inverse_matrix: Optional[List[List[float]]] = None

    if det != 0:
        inverse_matrix = [
            [
                (m11 * m22 - m12 * m21) / det,
                (m02 * m21 - m01 * m22) / det,
                (m01 * m12 - m02 * m11) / det
            ],
            [
                (m12 * m20 - m10 * m22) / det,
                (m00 * m22 - m02 * m20) / det,
                (m02 * m10 - m00 * m12) / det
            ],
            [
                (m10 * m21 - m11 * m20) / det,
                (m01 * m20 - m00 * m21) / det,
                (m00 * m11 - m01 * m10) / det
            ]
        ]
        
        inverse_matrix = [[round(val, 4) for val in row] for row in inverse_matrix]

    return {
        "determinant": round(det, 4),
        "inverse": inverse_matrix 
    }

SERVICE_REGISTRY = {
    "CHAR_COUNT": char_count,
    "WORD_COUNT": word_count,
    "REVERSE_STRING": reverse_string,
    "REMOVE_VOWELS": remove_vowels,
    "MATRIX_3X3": matrix_3x3
}
