import threading as thrdg
from definitions import *
from queue import Queue
import socket as skt
import argparse
import time


class Client:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.setblocking(0)

        self.SERVER_ADDR = (L_HOST, L_PORT)
        self.SESSION_ID = int()

        self.messages_recieved = Queue()
        self.messages_to_send = Queue()

    def run(self):
        self.init_threads()
        self.init_connection()

        self.messages_to_send.put(Header.create_reply(
            Operation.SQUARE, Status.SENDING, self.SESSION_ID, '12'))

        time.sleep(100)

        self.stop()

    def stop(self):
        self.kill_threads()
        self.socket.close()

    def init_connection(self):
        while True:
            self.messages_to_send.put(self.connection_request())

            if not self.messages_recieved.empty():
                self.SESSION_ID = self.messages_recieved.get().id
                break

            time.sleep(1)

    def sending_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            if not self.messages_to_send.empty():
                message = self.messages_to_send.get()
                self.socket.sendto(message, self.SERVER_ADDR)

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
                    print('Server recieved the request')
                    continue

                print('Recieved message from server:',
                      addr[0], 'through port:', addr[1])

                print(msg.to_string())
                self.messages_recieved.put(msg)

                # Potwierdzamy odbiór komunikatu
                self.messages_to_send.put(
                    self.std_client_response(msg.operation))

    def init_threads(self):
        self.recieve = thrdg.Thread(target=self.recieving_func)
        self.send = thrdg.Thread(target=self.sending_func)

        self.recieve.start()
        self.send.start()

    def kill_threads(self):
        self.recieve.run = False
        self.send.run = False

        self.recieve.join()
        self.send.join()

    def connection_request(self):
        return Header.create_reply(Operation.CONNECTING, Status.NONE, Status.NONE)

    def std_client_response(self, operation: str) -> bytes:
        return Header.create_reply(operation, Status.OK, self.SESSION_ID)


a = Client()
a.run()
