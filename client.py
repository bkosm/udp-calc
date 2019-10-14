import threading as thrdg
from definitions import *
from queue import Queue
import socket as skt
import argparse
import time
from collections import deque


class Client:
    def __init__(self):
        # Inicjalizacja nieblokującego gniazda na UDP
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.setblocking(0)

        self.parse_arguments()

        self.SERVER_ADDR = (self.arguments.ip_address, self.arguments.port)
        self.SESSION_ID = int()

        # Inicjalizacja bezpiecznych kontenerów
        self.messages_recieved = Queue()
        self.messages_to_send = Queue()
        self.requests = []

    def run(self):
        if self.init_connection():
            self.init_threads()
            self.process_arguments()

            while True:
                cond = input("Type in 'quit' to exit app\n")
                if cond == 'quit':
                    break

        self.stop()

    def stop(self):
        self.disconnect()
        self.kill_threads()
        self.socket.close()

    def init_connection(self) -> bool:
        print('Waiting for server connection')
        while True:
            # Wysyłamy prośbę o utworzenie sesji
            self.socket.sendto(self.connection_request(), self.SERVER_ADDR)
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

    def disconnect(self):
        self.messages_to_send.put(Header.create_reply(
            Operation.DISCONNECTING, Status.NONE, self.SESSION_ID))

        print('Quitting session, please wait')
        time.sleep(3)

    # Menu operacji
    def process_arguments(self):
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

        if self.arguments.sortA:
            while True:
                num = input(
                    "Enter next number to sort, if it's the last one, add '-' after the number (ex. '3-'):\n")

                if not num:
                    continue

                if num[-1] == '-':
                    req = Header(Operation.SORT_A, Status.LAST,
                                 self.SESSION_ID, Header.create_timestamp(), num[:1])

                    self.requests.append(req)
                    self.messages_to_send.put(req.to_send())

                    break
                else:
                    req = Header(Operation.SORT_A, Status.SENDING,
                                 self.SESSION_ID, Header.create_timestamp(), num[:1])

                    self.requests.append(req)
                    self.messages_to_send.put(req.to_send())

        elif self.arguments.sortD:
            while True:
                num = input(
                    "Enter next number to sort, if it's the last one, add '-' after the number (ex. '3-'):\n")

                if not num:
                    continue

                if num[-1] == '-':
                    self.messages_to_send.put(Header.create_reply(
                        Operation.SORT_D, Status.LAST, self.SESSION_ID, num[:1]))
                    break
                else:
                    self.messages_to_send.put(Header.create_reply(
                        Operation.SORT_D, Status.SENDING, self.SESSION_ID, num))

    def sending_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            if not self.messages_to_send.empty():
                message = self.messages_to_send.get()
                self.socket.sendto(message, self.SERVER_ADDR)

    def display_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            if not self.messages_recieved.empty() and self.requests:
                msg: Header = self.messages_recieved.get()

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

                #TODO print sorting

                if msg.operation == Operation.SORT_A:
                    for req in self.requests:
                        if msg.operation == req.operation:
                            print(msg.a)

                            self.requests.remove(req)

    def recieving_func(self):
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
                    print('Recieved message from server:',
                          addr[0], 'through port:', addr[1])
                    self.messages_recieved.put(msg)

                    # Potwierdzamy odbiór komunikatu
                    self.messages_to_send.put(
                        self.std_client_response(msg.operation))

    def init_threads(self):
        self.recieve = thrdg.Thread(target=self.recieving_func)
        self.send = thrdg.Thread(target=self.sending_func)
        self.display = thrdg.Thread(target=self.display_func)

        self.recieve.start()
        self.send.start()
        self.display.start()

    def kill_threads(self):
        self.recieve.run = False
        self.send.run = False
        self.display.run = False

        self.recieve.join()
        self.send.join()
        self.display.join()

    def connection_request(self) -> bytes:
        return Header.create_reply(Operation.CONNECTING, Status.NONE, Status.NONE)

    def std_client_response(self, operation: str) -> bytes:
        return Header.create_reply(operation, Status.OK, self.SESSION_ID)

    def parse_arguments(self):
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


a = Client()
a.run()
