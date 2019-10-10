'''
    Nagłówek protokołu:
    o->(x)#s->(x)#i->(x)#a->(x)#b->(x)#t->(x)
    o => operacja           s => status
    i => id sesji           a => liczba 1
    b => liczba 2           t => znacznik czasu
'''

from datetime import datetime as dt
import re

# Skrajne akceptowane wartości zmiennych
MAX_NR: int = 9223372036854775807
MIN_NR: int = -MAX_NR - 1

HEADER_REGEX: str = r"b'o->(.*)#s->(.*)#i->(.*)#a->(.*)#b->(.*)#t->(.*)'"


class Header:
    def __init__(self, o='', s='', i='', t='', a='null', b='null'):
        self.operation = str(o)
        self.status = str(s)
        self.id = str(i)
        self.timestamp = str(t)
        self.a = str(a)
        self.b = str(b)

    def to_string(self) -> str:
        return "o->"+self.operation+"#s->"+self.status+"#i->" + \
            self.id+"#a->"+self.a+"#b->"+self.b+"#t->"+self.timestamp+"#"

    def to_send(self) -> bytes:
        return bytes(self.to_string(), encoding='utf8')


class Operation:
    RANDOM = 'a'
    MODULO = 'A'
    SQUARE = 'b'
    MULTIPLY = 'B'
    SORT_A = 'c'
    SORT_D = 'C'


class Status:
    # Możliwe wartości pola status
    SENDING = 'sending'
    CONNECTING = 'connecting'
    RECIEVED = 'recieved'
    OUTPUT = 'output'
    LAST = 'last'
    OK = 'ok'


def create_timestamp() -> str:
    time = str(dt.utcnow().replace(microsecond=0))
    return re.sub('[- :]', '', time)



L_HOST: str = '127.0.0.1'
L_PORT: int = 65432