class CustomBaseConverter:
    def __init__(self) -> None:
        base62 = (
            [str(i) for i in range(10)] +
            [chr(ord('A') + i) for i in range(26)] +
            [chr(ord('a') + i) for i in range(26)]
        )
        self.prefixes = ["!", "@", "#", "$", "%", "^", "&", "*", "_", "~", "α", "β", "γ", "δ", "λ"]
        
        self.all_chars = base62.copy() + self.prefixes.copy()
        for prefix in self.prefixes:
            for char in base62:
                self.all_chars.append(prefix + char)

    def _get_alphabet_and_map(self, base: int) -> tuple[list, dict]:
        if not (2 <= base <= len(self.all_chars)):
            raise ValueError(f"Система счисления должна быть от 2 до {len(self.all_chars)}")
        
        current_alphabet = self.all_chars[:base]
        char_to_value = {char: i for i, char in enumerate(current_alphabet)}
        return current_alphabet, char_to_value

    def convert_any_base(self, number_str: str, from_base: int, to_base: int) -> str:
        if not number_str:
            raise ValueError("Пустая строка")

        alphabet_from, map_from = self._get_alphabet_and_map(from_base)
        alphabet_to, _ = self._get_alphabet_and_map(to_base)

        decimal_value = 0
        i = 0
        while i < len(number_str):
            current_char = number_str[i]
            if current_char in self.prefixes:
                if i + 1 < len(number_str):
                    combined = number_str[i:i+2]
                    if combined in map_from:
                        decimal_value = decimal_value * from_base + map_from[combined]
                        i += 2
                        continue
                    else:
                        raise ValueError(f"Составной символ '{combined}' не входит в {from_base}-ричную систему")
                else:
                    raise ValueError(f"Строка завершилась префиксом '{current_char}' без смыслового символа")

            if current_char in map_from:
                decimal_value = decimal_value * from_base + map_from[current_char]
                i += 1
            else:
                raise ValueError(f"Символ '{current_char}' не входит в {from_base}-ричную систему")

        if decimal_value == 0:
            return alphabet_to[0]

        res = []
        while decimal_value > 0:
            res.append(alphabet_to[decimal_value % to_base])
            decimal_value //= to_base

        return "".join(reversed(res))

    def system_to_text(self, number_str: str, from_base: int) -> tuple[str, str]:
        decimal_str = self.convert_any_base(number_str, from_base=from_base, to_base=10)
        decimal_number = int(decimal_str)

        binary_str = bin(decimal_number)[2:]

        while len(binary_str) % 8 != 0:
            binary_str = "0" + binary_str

        text_bytes = bytearray()
        for i in range(0, len(binary_str), 8):
            text_bytes.append(int(binary_str[i:i+8], 2))

        try:
            decoded_text = text_bytes.decode('utf-8', errors='replace')
        except Exception:
            decoded_text = "[Ошибка декодирования UTF-8]"

        return binary_str, decoded_text
    
    def text_to_system(self, input_text: str, to_base: int) -> tuple[str, str]:
        if not input_text:
            raise ValueError("Пустая строка текста")

        text_bytes = input_text.encode('utf-8')
        binary_str = "".join(f"{b:08b}" for b in text_bytes)

        decimal_number = int(binary_str, 2)

        system_res = self.convert_any_base(str(decimal_number), from_base=10, to_base=to_base)

        return binary_str, system_res