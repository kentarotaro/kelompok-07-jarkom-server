import random
import copy
from typing import Any

class FaultInjector:
    @staticmethod
    def apply(service: str, result: Any, rate: float = 0.30) -> Any:
        if random.random() >= rate:
            return result

        try:
            if service == "CHAR_COUNT":
                delta = random.choice([-3, -2, -1, 1, 2, 3, 5])
                return max(0, result + delta)
            
            elif service == "WORD_COUNT":
                delta = random.choice([-2, -1, 1, 2, 3])
                return max(0, result + delta)
            
            elif service == "REVERSE_STRING":
                corrupted_result = result[::-1]
                if corrupted_result == result:
                    return result + "s"
                return corrupted_result
            
            elif service == "REMOVE_VOWELS":
                vowels = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
                return result + random.choice(vowels)
            
            elif service == "MATRIX_3X3":
                if isinstance(result, dict):
                    corrupted = copy.deepcopy(result)
                    if corrupted.get("determinant") is not None:
                        corrupted["determinant"] = round(corrupted["determinant"] + random.uniform(2.0, 10.0), 4)
                    if corrupted.get("inverse") and len(corrupted["inverse"]) == 3:
                        corrupted["inverse"][0][0] = round(corrupted["inverse"][0][0] +5.0, 4)
                    return corrupted
                return result

        except Exception as e:
            print(f"[FAULT INJECTION ERROR] '{service}': {e}")
            return result

        return result