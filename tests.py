from calculations import *
import argparse

# Testy jednostkowe funkcji


def test_operations():
    assert Calculations.randomint_between('1', '2') == '2'
    assert Calculations.modulo('10', '3') == '1'
    assert Calculations.square('2') == '4'
    assert Calculations.multiply('2', '3') == '6'


# Miejsce do testowania rozwiązań
