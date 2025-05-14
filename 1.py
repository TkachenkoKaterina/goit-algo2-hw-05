import hashlib

class BloomFilter:
    def __init__(self, size=1000, num_hashes=3):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def _hashes(self, item):
        hashes = []
        for i in range(self.num_hashes):
            # Створюємо хеши на основі SHA-256 з додатковим індексом i
            hash_input = f"{item}_{i}".encode("utf-8")
            hash_digest = hashlib.sha256(hash_input).hexdigest()
            index = int(hash_digest, 16) % self.size
            hashes.append(index)
        return hashes

    def add(self, item):
        if not isinstance(item, str) or item.strip() == "":
            return  # ігнорування порожніх або некоректних значень
        for index in self._hashes(item):
            self.bit_array[index] = 1

    def contains(self, item):
        if not isinstance(item, str) or item.strip() == "":
            return False
        return all(self.bit_array[index] for index in self._hashes(item))


def check_password_uniqueness(bloom_filter, passwords):
    result = {}
    for password in passwords:
        if not isinstance(password, str) or password.strip() == "":
            result[password] = "некоректний"
        elif bloom_filter.contains(password):
            result[password] = "вже використаний"
        else:
            result[password] = "унікальний"
            bloom_filter.add(password)
    return result


# Приклад використання
if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")