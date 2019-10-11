'''
    Nagłówek protokołu:
    o->(x)#s->(x)#i->(x)#a->(x)#b->(x)#t->(x)
    o => operacja           s => status
    i => id sesji           a => liczba 1
    b => liczba 2           t => znacznik czasu
'''

from datetime import datetime as dt
from queue import Queue
import re

# Skrajne akceptowane wartości zmiennych
MAX_NR: int = 9223372036854775807
MIN_NR: int = -MAX_NR - 1

HEADER_REGEX: str = r"b'o->(.*)#s->(.*)#i->(.*)#a->(.*)#b->(.*)#t->(.*)'"

L_HOST: str = '127.0.0.1'
L_PORT: int = 65432

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

    @staticmethod
    def to_list() -> list:
        return [Operation.RANDOM, Operation.MODULO, Operation.SQUARE, Operation.MULTIPLY, Operation.SORT_A, Operation.SORT_D]


class Status:
    # Możliwe wartości pola status
    SENDING = 'sending'
    CONNECTING = 'connecting'
    RECIEVED = 'recieved'
    OUTPUT = 'output'
    LAST = 'last'
    OK = 'ok'

    @staticmethod
    def to_list() -> list:
        return [Status.SENDING, Status.CONNECTING, Status.RECIEVED, Status.OUTPUT, Status.LAST, Status.OK]


class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.numbers_to_sort = []
        self.request_queue = Queue()


def create_timestamp() -> str:
    time = str(dt.utcnow().replace(microsecond=0))
    return re.sub('[- :]', '', time)


# Function that turns the protocol message into an organized struct
def parse_message(message: str) -> Header:
    # example=> b'o->A#s->ok#i->xdxdxdxdx#a->null#b->null#t->20191010134342#'
    groups = re.match(HEADER_REGEX, message)

    if groups:
        operation = ''
        status = ''

        for op in Operation.to_list():
            if op == groups.group(1):
                operation = op
        for st in Status.to_list():
            if st == groups.group(2):
                status = st

        return Header(operation, status, groups.group(3), groups.group(6), groups.group(4), groups.group(5))

    return None


