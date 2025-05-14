import re
import time
import mmh3
import math


class HyperLogLog:
    def __init__(self, p=10):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._get_alpha()
        self.small_range_correction = 5 * self.m / 2

    def _get_alpha(self):
        # Емпіричні значення для малих m
        if self.p == 4:      # m = 16
            return 0.673
        elif self.p == 5:    # m = 32
            return 0.697
        elif self.p == 6:    # m = 64
            return 0.709
        # Загальна формула для інших m
        return 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        x = mmh3.hash(str(item), signed=False)
        j = x & (self.m - 1)
        w = x >> self.p
        self.registers[j] = max(self.registers[j], self._rho(w))

    def _rho(self, w):
        if w == 0:
            return 32
        return (len(bin(w)) - 2)

    def count(self):
        Z = sum(2.0 ** -r for r in self.registers)
        E = self.alpha * self.m * self.m / Z

        if E <= self.small_range_correction:
            V = self.registers.count(0)
            if V > 0:
                return self.m * math.log(self.m / V)
        return E


def load_ips(log_path):
    pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ips = []
    with open(log_path, 'r') as f:
        for line in f:
            m = pattern.search(line)
            if m:
                ips.append(m.group())
    return ips


def main():
    log_path = 'lms-stage-access.log'
    ips = load_ips(log_path)

    # --- Точний підрахунок ---
    start_exact = time.perf_counter()
    unique_exact = len(set(ips))
    time_exact = time.perf_counter() - start_exact

    # --- HyperLogLog ---
    hll = HyperLogLog(p=10)
    start_hll = time.perf_counter()
    for ip in ips:
        hll.add(ip)
    unique_hll = hll.count()
    time_hll = time.perf_counter() - start_hll

    # --- Вивід результатів ---
    print("Результати порівняння продуктивності:")
    print(f"{'Метод':<25}{'Унікальні елементи':>20}{'Час (сек)':>15}")
    print("-" * 60)
    print(f"{'Точний підрахунок':<25}{unique_exact:>20}{time_exact:>15.6f}")
    print(f"{'HyperLogLog (mmh3)':<25}{unique_hll:>20.2f}{time_hll:>15.6f}")


if __name__ == "__main__":
    main()
