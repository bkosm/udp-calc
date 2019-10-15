from definitions import Operation, Status, Header
from queue import Queue
import threading as thrdg
import socket as skt
import argparse
import time


class Client:
    def __init__(self):
        # Inicjalizacja nieblokującego gniazda na UDP
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.setblocking(0)

        self.parse_arguments()

        self.SERVER_ADDR = (self.arguments.ip_address, self.arguments.port)
        self.SESSION_ID = Status.NONE

        # Inicjalizacja bezpiecznych kontenerów
        self.messages_recieved = Queue()
        self.messages_to_send = Queue()
        self.requests = []

    def run(self) -> None:
        if self.init_connection():
            self.init_threads()

            self.process_arguments()

            self.disconnect()
            self.kill_threads()
        self.socket.close()

    def init_connection(self) -> bool:
        print('Waiting for server connection')
        while True:
            # Wysyłamy prośbę o utworzenie sesji
            self.socket.sendto(Header.create_reply(
                Operation.CONNECTING, Status.NONE, self.SESSION_ID), self.SERVER_ADDR)
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
                    print('Server recieved request (op={})'.format(msg.operation))

                else:
                    if msg.operation == Operation.SORT_A or msg.operation == Operation.SORT_D:
                        print(msg.a)

                    else:
                        self.print_result(msg)

                    # Potwierdzamy odbiór komunikatu
                    self.messages_to_send.put(
                        self.std_client_response(msg.operation))

    def std_client_response(self, operation: str) -> bytes:
        return Header.create_reply(operation, Status.OK, self.SESSION_ID)

    def print_result(self, msg: Header) -> None:
        if self.requests:
            if msg.operation == Operation.SQUARE:
                for req in self.requests:
                    if msg.operation == req.operation:
                        print("{}^2 = {}".format(req.a, msg.a))
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

    # Menu operacji
    def process_arguments(self) -> None:
        # Operacje wywoływane jako argumenty programu realizujemy od razu
        if self.arguments.square:
            req = Header(Operation.SQUARE, Status.NONE, self.SESSION_ID,
                         Header.create_timestamp(), self.arguments.square)

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())

        if self.arguments.multiply:
            req = Header(Operation.MULTIPLY, Status.NONE, self.SESSION_ID,
                         Header.create_timestamp(), self.arguments.multiply[0], self.arguments.multiply[1])

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())

        if self.arguments.random:
            req = Header(Operation.RANDOM, Status.NONE, self.SESSION_ID,
                         Header.create_timestamp(), self.arguments.random[0], self.arguments.random[1])

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())

        if self.arguments.modulo:
            req = Header(Operation.MODULO, Status.NONE, self.SESSION_ID,
                         Header.create_timestamp(), self.arguments.modulo[0], self.arguments.modulo[1])

            self.requests.append(req)
            self.messages_to_send.put(req.to_send())

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
            Operation.DISCONNECTING, Status.NONE, self.SESSION_ID))

        print('Quitting session, please wait')
        time.sleep(3)

    def kill_threads(self) -> None:
        self.recieve.run = False
        self.send.run = False

        self.recieve.join()
        self.send.join()

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(
            description="Connect to a remote host and perform calculations.")

        parser.add_argument(
            "ip_address", help="IP Address of the server.")
        parser.add_argument(
            "port", type=int, help="Port through which the data will be sent.")

        parser.add_argument("-s", "--square", required=False,
                            help="Calculate square of a number", metavar="N")
        parser.add_argument("-m", "--multiply", required=False,
                            help="Multiply two numbers", metavar="N", nargs=2)
        parser.add_argument("-r", "--random", required=False,
                            help="Get a random number from range (inclusive)", metavar="N", nargs=2)
        parser.add_argument("-M", "--modulo", required=False,
                            help="Get modulo operation result", metavar="N", nargs=2)

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-x", "--sortA", required=False,
                           help="Sort given numbers in ascending order", action="store_true")
        group.add_argument("-X", "--sortD", required=False,
                           help="Sort given numbers in descending order", action="store_true")

        self.arguments = parser.parse_args()


if __name__ == '__main__':
    app = Client()
    app.run()
