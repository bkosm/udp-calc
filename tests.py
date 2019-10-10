from calculations import *
from definitions import *


# Testy jednostkowe funkcji
def test_operations():
    assert Calculations.randomint_between('1', '2') == '2'
    assert Calculations.modulo('10', '3') == '1'
    assert Calculations.square('2') == '4'
    assert Calculations.multiply('2', '3') == '6'
    assert parse_message("b'o->A#s->ok#i->xdxdxdxdx#a->null#b->null#t->20191010134342#'").to_send(
    ) == b'o->A#s->ok#i->xdxdxdxdx#a->null#b->null#t->20191010134342##'
