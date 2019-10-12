from random import randint as rd

# Skrajne akceptowane wartości zmiennych
MAX_NR: int = 9223372036854775807
MIN_NR: int = -MAX_NR - 1


class Calculations:
    @staticmethod
    def randomint_between(a: str, b: str) -> str:
        result = rd(int(a) + 1, int(b))

        if result < MIN_NR or result > MAX_NR:
            raise OverflowError

        return str(result)

    @staticmethod
    def modulo(a: str, b: str) -> str:
        if int(b) == 0:
            raise ZeroDivisionError

        result = int(a) % int(b)
        if result < MIN_NR or result > MAX_NR:
            raise OverflowError

        return str(result)

    @staticmethod
    def square(a: str) -> str:
        result = int(a)**2

        if result < MIN_NR or result > MAX_NR:
            raise OverflowError

        return str(result)

    @staticmethod
    def multiply(a: str, b: str) -> str:
        result = int(a) * int(b)

        if result < MIN_NR or result > MAX_NR:
            raise OverflowError

        return str(result)

    @staticmethod
    def sort(numbers: list, reverse: bool = False) -> str:
        if len(numbers) == 1:
            return numbers

        to_sort = []
        for n in numbers:
            num = int(n)
            if num > MAX_NR or num < MIN_NR:
                raise OverflowError
            else:
                to_sort.append(num)

        if not reverse:
            to_sort.sort()
        else:
            to_sort.sort(reverse=True)

        return [str(i) for i in to_sort]
