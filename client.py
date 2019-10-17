from definitions import Operation, Status, Header
from queue import Queue
import threading as thrdg
import socket as skt
import argparse
import time
import re


class Client:
    def __init__(self):
        # Inicjalizacja nieblokującego gniazda na UDP
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.setblocking(0)

        self.use_menu = self.parse_arguments()

        self.SERVER_ADDR = (self.arguments.ip_address, self.arguments.port)
        self.SESSION_ID = Status.NONE

        # Inicjalizacja bezpiecznych kontenerów
        self.messages_recieved = Queue()
        self.messages_to_send = Queue()
        self.requests = []

    def run(self) -> None:
        if self.init_connection():
            self.init_threads()

            if self.use_menu:
                self.menu_loop()
            else:
                self.process_arguments()

            self.disconnect()
            self.kill_threads()
        self.socket.close()

    def init_connection(self) -> bool:
        print('Waiting for server connection')
        while True:
            # Wysyłamy prośbę o utworzenie sesji
            msg = Header.create_reply(
                operation=Operation.CONNECTING, session_id=self.SESSION_ID)

            self.socket.sendto(msg, self.SERVER_ADDR)
            time.sleep(0.5)

            # Czekamy na potwierdzenie serwera lub informację o zajętości
            while True:
                try:
                    msg, addr = self.socket.recvfrom(1024)
                    msg = Header.parse_message(repr(msg))

                    if msg.status == Status.OK:
                        self.SESSION_ID = msg.id
                        print('Connected to server')
                        return True
                    elif msg.status == Status.BUSY:
                        print(
                            'Server is busy, cannot connect right now\nExiting client app')
                        return False
                except:
                    break

    def init_threads(self) -> None:
        self.send = thrdg.Thread(target=self.sending_func)
        self.recieve = thrdg.Thread(target=self.recieving_func)

        self.send.start()
        self.recieve.start()

    def sending_func(self) -> None:
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            if not self.messages_to_send.empty():
                message = self.messages_to_send.get()
                self.socket.sendto(message, self.SERVER_ADDR)

    def recieving_func(self) -> None:
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                continue

            if data:
                msg = Header.parse_message(repr(data))
                # Jeśli wiadomość to potwierdzenie drukujemy
                # informację i nie dodajemy jej do kolejki
                if msg.status == Status.RECIEVED:
                    print('Server recieved request')

                else:
                    if msg.operation == Operation.SORT_A or msg.operation == Operation.SORT_D:
                        print(msg.a)

                    else:
                        self.print_result(msg)

                    # Potwierdzamy odbiór komunikatu
                    self.messages_to_send.put(
                        Header.create_reply(msg.operation, Status.OK, self.SESSION_ID))

    def print_result(self, msg: Header) -> None:
        if self.requests:
            if msg.operation == Operation.ADD:
                for req in self.requests:
                    if msg.operation == req.operation:
                        print("{} + {} = {}".format(req.a, req.b, msg.a))
                        self.requests.remove(req)

            if msg.operation == Operation.MULTIPLY:
                for req in self.requests:
                    if msg.operation == req.operation:
                        print("{} * {} = {}".format(req.a, req.b, msg.a))
                        self.requests.remove(req)

            if msg.operation == Operation.RANDOM:
                for req in self.requests:
                    if msg.operation == req.operation:
                        print("random between <{}; {}> = {}".format(
                            req.a, req.b, msg.a))
                        self.requests.remove(req)

            if msg.operation == Operation.MODULO:
                for req in self.requests:
                    if msg.operation == req.operation:
                        print("{} % {} = {}".format(req.a, req.b, msg.a))
                        self.requests.remove(req)

    # Menu operacji w pętli programu
    def menu_loop(self) -> None:
        print("""
Enter the operations that you wish to perform in natural form (ex. 2 + 2)
Possible operations are:
addition        -> x + y
multiplication  -> x * y
modulo          -> x % y
random integer  -> x ; y
sort ascending  -> sortA
sort descending -> sortD
quit session    -> quit""")

        operation = ''
        exp = r"(\d*)\s*(\+|%|\*|;)\s*(\d*)"

        while True:
            operation = input()

            match = re.match(exp, operation)

            if match:
                if match.group(2) == '+':
                    self.arguments.add = [
                        int(match.group(1)), int(match.group(3))]
                elif match.group(2) == '*':
                    self.arguments.multiply = [
                        int(match.group(1)), int(match.group(3))]
                elif match.group(2) == '%':
                    self.arguments.modulo = [
                        int(match.group(1)), int(match.group(3))]
                elif match.group(2) == ';':
                    self.arguments.random = [
                        int(match.group(1)), int(match.group(3))]

            elif operation == 'sortA':
                self.collect_sortA_request()

            elif operation == 'sortD':
                self.collect_sortD_request()

            elif operation == 'quit':
                break

            else:
                print('Invalid expression')
                continue

            self.process_arguments()

    # Menu operacji z linii komend

    def process_arguments(self) -> None:
        # Operacje wywoływane jako argumenty programu realizujemy od razu
        if self.arguments.add:
            req = Header(o=Operation.ADD, i=self.SESSION_ID,
                         t=Header.create_timestamp(), a=str(self.arguments.add[0]), b=str(self.arguments.add[1]))

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())
            self.arguments.add = None

        if self.arguments.multiply:
            req = Header(o=Operation.MULTIPLY, i=self.SESSION_ID,
                         t=Header.create_timestamp(), a=str(self.arguments.multiply[0]), b=str(self.arguments.multiply[1]))

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())
            self.arguments.multiply = None

        if self.arguments.random:
            req = Header(o=Operation.RANDOM, i=self.SESSION_ID,
                         t=Header.create_timestamp(), a=str(self.arguments.random[0]), b=str(self.arguments.random[1]))

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())
            self.arguments.random = None

        if self.arguments.modulo:
            req = Header(o=Operation.MODULO, i=self.SESSION_ID,
                         t=Header.create_timestamp(), a=str(self.arguments.modulo[0]), b=str(self.arguments.modulo[1]))

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())
            self.arguments.modulo = None

        # Sortowanie przetwarzamy w pętli wewnątrz programu
        if self.arguments.sortA:
            self.collect_sortA_request()
        elif self.arguments.sortD:
            self.collect_sortD_request()

    def collect_sortA_request(self) -> None:
        print("Enter next number to sort, if it's the last one, add '-' after the number (ex. '3-'):")
        while True:
            num = input()

            if not num:
                print('not num')
                continue

            if num[-1] == '-':
                self.messages_to_send.put(Header.create_reply(
                    Operation.SORT_A, Status.LAST, self.SESSION_ID, num[:-1]))
                return
            else:
                self.messages_to_send.put(Header.create_reply(
                    Operation.SORT_A, Status.SENDING, self.SESSION_ID, num))

    def collect_sortD_request(self) -> None:
        print("Enter next number to sort, if it's the last one, add '-' after the number (ex. '3-'):")
        while True:
            num = input()

            if not num:
                continue

            if num[-1] == '-':
                self.messages_to_send.put(Header.create_reply(
                    Operation.SORT_D, Status.LAST, self.SESSION_ID, num[:-1]))
                return
            else:
                self.messages_to_send.put(Header.create_reply(
                    Operation.SORT_D, Status.SENDING, self.SESSION_ID, num))

    # Wysyłamy żądanie rozłączenia i oczekujemy na otrzymanie pozostałych wiadomości
    def disconnect(self) -> None:
        self.messages_to_send.put(Header.create_reply(
            operation=Operation.DISCONNECTING, session_id=self.SESSION_ID))

        print('Quitting session, please wait')
        time.sleep(1)

    def kill_threads(self) -> None:
        self.recieve.run = False
        self.send.run = False

        self.recieve.join()
        self.send.join()

    def parse_arguments(self) -> bool:
        parser = argparse.ArgumentParser(
            description="Connect to a remote host and perform calculations.")

        parser.add_argument(
            "ip_address", help="IP Address of the server.")
        parser.add_argument(
            "port", type=int, help="Port through which the data will be sent.")

        parser.add_argument("-a", "--add", required=False,
                            help="Calculate the sum of two numbers", metavar="N", nargs=2, type=int)
        parser.add_argument("-m", "--multiply", required=False,
                            help="Multiply two numbers", metavar="N", nargs=2, type=int)
        parser.add_argument("-r", "--random", required=False,
                            help="Get a random number from range (inclusive)", metavar="N", nargs=2, type=int)
        parser.add_argument("-M", "--modulo", required=False,
                            help="Get modulo operation result", metavar="N", nargs=2, type=int)

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-x", "--sortA", required=False,
                           help="Sort given numbers in ascending order", action="store_true")
        group.add_argument("-X", "--sortD", required=False,
                           help="Sort given numbers in descending order", action="store_true")

        self.arguments = parser.parse_args()

        if not self.arguments.add and not self.arguments.multiply and not self.arguments.random and not self.arguments.modulo and not self.arguments.sortA and not self.arguments.sortD:
            return True
        else:
            return False


if __name__ == '__main__':
    app = Client()
    app.run()
