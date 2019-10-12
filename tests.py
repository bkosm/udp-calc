from calculations import *
import argparse

# Testy jednostkowe funkcji


def test_operations():
    assert Calculations.randomint_between('1', '2') == '2'
    assert Calculations.modulo('10', '3') == '1'
    assert Calculations.square('2') == '4'
    assert Calculations.multiply('2', '3') == '6'


# Miejsce do testowania rozwiązań

class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Connect to a remote host and perform calculations.")

        self.parser.add_argument(
            'ip_address', help='IP Address of the server.')
        self.parser.add_argument(
            'port', type=int, help='Port through which the data will be sent.')


        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            '-s', '--square', help='Calculate the square of given number.')

        group.add_argument(
            '-m', '--multiply', help='Multiply two numbers.')

        group.add_argument(
            '-rnd', '--random', help='Get a random number between given values (inclusive).')

        group.add_argument(
            '-r', '--randomint', help='Get a random number between given values (inclusive).')

        self.args = self.parser.parse_args()

        print(self.args.ip_address)
        print(self.args.port)
        print(self.args.square)


a = ArgParser()
