from random import randint as rd


def randomint_between(a: str, b: str) -> str:
    return str(rd(int(a) + 1, int(b)))


def modulo(a: str, b: str) -> str:
    return str(int(a) % int(b))

def sort(numbers: list[int]) -> str:

    pass

# Testy jednostkowe funkcji
def test_operations():
    assert randomint_between('1', '2') == '2'
    assert modulo('10', '3') == '1'
