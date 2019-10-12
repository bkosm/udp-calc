from random import randint as rd


class Calculations:
    @staticmethod
    def randomint_between(a: str, b: str) -> str:
        return str(rd(int(a) + 1, int(b)))

    @staticmethod
    def modulo(a: str, b: str) -> str:
        if int(b) == 0:
            raise ZeroDivisionError
        else:
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
