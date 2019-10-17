'''

    Nagłówek protokołu:
    o->(x)#s->(x)#i->(x)#a->(x)#b->(x)#t->(x)#

    o => operacja           s => status
    i => id sesji           a => liczba 1
    b => liczba 2           t => znacznik czasu

'''

from calculations import Calculations
from datetime import datetime as dt
from copy import deepcopy as dc
from queue import Queue
import re


HEADER_REGEX: str = r"b'(o->(.)#)*(s->(.*)#)*i->(\d*|null)#(a->(\d*|null)#)*(b->(\d*|null)#)*t->(\d*)#'"

L_HOST: str = '127.0.0.1'
L_PORT: int = 65432


class Operation:
    RANDOM = 'a'
    MODULO = 'A'
    ADD = 'b'
    MULTIPLY = 'B'
    SORT_A = 'c'
    SORT_D = 'C'
    CONNECTING = 'x'
    DISCONNECTING = 'X'

    @staticmethod
    def to_list() -> list:
        return [Operation.RANDOM, Operation.MODULO, Operation.ADD, Operation.MULTIPLY, Operation.SORT_A, Operation.SORT_D, Operation.CONNECTING, Operation.DISCONNECTING]


class Status:
    SENDING = 'send'
    CONNECTING = 'conn'
    RECIEVED = 'recvd'
    OUTPUT = 'output'
    LAST = 'last'
    ERROR = 'err'
    BUSY = 'busy'
    OK = 'ok'
    NONE = 'null'

    @staticmethod
    def to_list() -> list:
        return [Status.SENDING, Status.CONNECTING, Status.RECIEVED, Status.OUTPUT, Status.LAST, Status.ERROR, Status.BUSY, Status.OK, Status.NONE]


class Header:
    def __init__(self, o=None, s=None, i=None, t=None, a=None, b=None):
        self.operation = o
        self.status = s
        self.id = i
        self.timestamp = t
        self.a = a
        self.b = b

    def to_string(self) -> str:
        msg = ''
        if self.operation:
            msg += "o->"+str(self.operation)+"#"

        if self.status:
            msg += "s->"+str(self.status)+"#"

        msg += "i->"+str(self.id)+"#"

        if self.a:
            msg += "a->"+str(self.a)+"#"

        if self.b:
            msg += "b->"+str(self.b)+"#"

        return msg+"t->"+str(self.timestamp)+"#"

    def to_send(self) -> bytes:
        print(self.to_string())
        return bytes(self.to_string(), encoding='utf8')

    @staticmethod
    def create_timestamp() -> str:
        time = str(dt.utcnow().replace(microsecond=0))[2:]
        return re.sub('[- :]', '', time)

    @staticmethod
    def create_reply(operation: str = None, status: str = None, session_id: str = None, num_a=None, num_b=None) -> bytes:
        return Header(operation, status, session_id, Header.create_timestamp(), num_a, num_b).to_send()

    # Funkcja przetwarzająca łańcuch tekstowy na strukturę nagłówka
    @staticmethod
    def parse_message(message: str):
        # example=> b'o->A#s->ok#i->11111#a->null#b->null#t->191010134342#'
        groups = re.match(HEADER_REGEX, message)

        if groups:
            operation = ''
            status = ''

            for op in Operation.to_list():
                if op == groups.group(2):
                    operation = op
                    break
            else:
                operation = Status.NONE

            for st in Status.to_list():
                if st == groups.group(4):
                    status = st
                    break
            else:
                status = Status.NONE

            return Header(operation, status, groups.group(5), groups.group(10), groups.group(7), groups.group(9))

        return Header(Status.ERROR, Status.ERROR, Status.ERROR, Status.ERROR)


class Session:
    def __init__(self, session_id: str, address: tuple):
        # Sesja zawiera ID klienta i jego adres
        self.session_id = session_id
        self.receiver_addr = address

        # Inicjalizacja tablicy liczb do sortowania oraz kolejki żądań
        self.numbers_to_sort = []
        self.request_queue = Queue()

    def request_to_response(self) -> list:
        # Jeśli są żadania, bierzemy pierwsze w kolejności i przetwarzamy je
        if not self.request_queue.empty():
            request: Header = self.request_queue.get()

            # Obsługujemy wymagane błędy przepełnienia
            try:
                # Potwierdzamy utworzenie sesji
                if request.operation == Operation.CONNECTING:
                    request.status = Status.OK

                elif request.operation == Operation.MODULO:
                    request.a = Calculations.modulo(request.a, request.b)
                    request.status = None
                    request.b = None

                elif request.operation == Operation.MULTIPLY:
                    request.a = Calculations.multiply(request.a, request.b)
                    request.status = None
                    request.b = None

                elif request.operation == Operation.RANDOM:
                    request.a = Calculations.randomint_between(
                        request.a, request.b)
                    request.status = None
                    request.b = None

                elif request.operation == Operation.ADD:
                    request.a = Calculations.add(request.a, request.b)
                    request.status = None
                    request.b = None

                # Przyjmujemy naraz operacje sortowania w obie strony i obie flagi sortowania
                elif request.operation == Operation.SORT_A or request.operation == Operation.SORT_D:
                    if request.status == Status.SENDING or request.status == Status.LAST:

                        self.numbers_to_sort.append(request.a)
                        last_sort = False

                        sorted_nums = []
                        if request.operation == Operation.SORT_A:
                            sorted_nums = Calculations.sort(
                                self.numbers_to_sort)
                        else:
                            sorted_nums = Calculations.sort(
                                self.numbers_to_sort, reverse=True)

                        if request.status == Status.LAST:
                            self.numbers_to_sort = []
                            last_sort = True

                        request.status = None
                        request.b = None
                        request.timestamp = Header.create_timestamp()

                        # Z posortowanych liczb tworzymy listę odpowiedzi
                        message_list = []
                        for num in sorted_nums:
                            request.a = num
                            message_list.append(dc(request))

                        return [(msg.to_send(), self.receiver_addr) for msg in message_list]

            except:
                self.numbers_to_sort = []
                request.status = Status.ERROR
                request.operation = None
                request.a = None

            # Wynik działań poza sortowaniem zwracamy tym samym sposobem
            request.timestamp = Header.create_timestamp()
            return [(request.to_send(), self.receiver_addr)]
