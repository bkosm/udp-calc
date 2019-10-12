import socket as skt
import threading as thrdg
from definitions import *
from queue import Queue
from random import randint
import time


class Server:
    def __init__(self):
        # Inicjalizacja nieblokującego gniazda na UDP
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind((L_HOST, L_PORT))
        self.socket.setblocking(0)

        # Inicjalizacja bezpiecznych kontenerów
        self.sending_queue = Queue()
        self.sessions = []

    # Funkcja dla osobnego wątku do odbierania i przetwarzania
    # wiadomości na sesje i żądania
    def recieve_func(self):
        this_thread = thrdg.currentThread()
        while getattr(this_thread, 'run', True):
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                continue

            if data:
                print('Recieved from:', addr[0], 'through port:', addr[1])

                message = repr(data)
                self.parse_request(message, addr)

    # Funkcja dla osobnego wątku do wysyłania
    # przetworzonych żądań
    def sending_func(self):
        this_thread = thrdg.currentThread()
        while getattr(this_thread, 'run', True):
            if not self.sending_queue.empty():
                try:
                    msg, addr = self.sending_queue.get()
                    self.socket.sendto(msg, addr)
                except:
                    continue

    # Funkcja dla osobnego wątku do wysyłania
    # przetworzonych żądań
    def operation_func(self):
        this_thread = thrdg.currentThread()
        while getattr(this_thread, 'run', True):
            time.sleep(0.1)
            for s in self.sessions:
                self.sending_queue.put(s.request_to_response())

    # Przetwarza wiadomość i rozdziela żądania na sesje
    def parse_request(self, message, addr):
        request = Header.parse_message(message)

        if not request.operation == Status.ERROR:
            if request.id == Status.NONE:
                request.id = str(randint(0, 99999)).rjust(5, "0")

            for s in self.sessions:
                if s.session_id == request.id:
                    s.request_queue.put(request)
                    break
            else:
                new_session = Session(request.id, addr)
                new_session.request_queue.put(request)
                self.sessions.append(new_session)

        self.sending_queue.put((self.std_server_response(request), addr))

    def run(self):
        self.init_threads()

        time.sleep(10)

        self.kill_threads()

    def stop(self):
        self.socket.close()

        print("Remaining requests:")
        for s in self.sessions:
            print('In session', s.session_id, ':')
            for i in list(s.request_queue.queue):
                print(i.to_string())

    def std_server_response(self, request: Header) -> bytes:
        request.status = Status.RECIEVED
        request.timestamp = Header.create_timestamp()

        return request.to_send()

    # Rozpoczynanie i kończenie wątków
    def init_threads(self):
        self.process_requests = thrdg.Thread(target=self.recieve_func)
        self.create_responses = thrdg.Thread(target=self.operation_func)
        self.send_messages = thrdg.Thread(target=self.sending_func)

        self.process_requests.start()
        self.create_responses.start()
        self.send_messages.start()

    def kill_threads(self):
        self.process_requests.run = False
        self.create_responses.run = False
        self.send_messages.run = False

        self.process_requests.join()
        self.create_responses.join()
        self.send_messages.join()


a = Server()
a.run()
a.stop()
