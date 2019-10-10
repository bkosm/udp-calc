from random import randint as rd


class Calculations:
    @staticmethod
    def randomint_between(a: str, b: str) -> str:
        return str(rd(int(a) + 1, int(b)))

    @staticmethod
    def modulo(a: str, b: str) -> str:
        return str(int(a) % int(b))

    @staticmethod
    def square(a: str) -> str:
        return str(int(a)**2)

    @staticmethod
    def multiply(a: str, b: str) -> str:
        return str(int(a) * int(b))

    @staticmethod
    def sort(numbers: list) -> str:

        pass

    @staticmethod
    def sort_reverse(numbers: list) -> str:

        pass


# Testy jednostkowe funkcji
def test_operations():
    assert Calculations.randomint_between('1', '2') == '2'
    assert Calculations.modulo('10', '3') == '1'
    assert Calculations.square('2') == '4'
    assert Calculations.multiply('2', '3') == '6'
