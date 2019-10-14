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
        self.session = None

    def run(self):
        self.init_threads()

        # Pętla wątku głównego
        while True:
            terminate = input(
                "Type in 'kill' anytime to terminate server process\n")
            if terminate == 'kill':
                break

        self.stop()

    def stop(self):
        self.kill_threads()
        self.socket.close()

        print("Remaining requests:")
        if self.session:
            print('In session', self.session.session_id, ':')
            for i in list(self.session.request_queue.queue):
                print(i.to_string())

    def init_threads(self):
        self.recieve = thrdg.Thread(target=self.recieving_func)
        self.operate = thrdg.Thread(target=self.operation_func)
        self.send = thrdg.Thread(target=self.sending_func)

        self.recieve.start()
        self.operate.start()
        self.send.start()

    def kill_threads(self):
        self.recieve.run = False
        self.operate.run = False
        self.send.run = False

        self.recieve.join()
        self.operate.join()
        self.send.join()

    # Funkcja dla osobnego wątku do przeprowadzania operacji
    # i kolejkowania ich wyników do wysłania

    def operation_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            time.sleep(0.1)

            # Wśród wszystkich sesji wykonuje metodę przetwarzania żądania
            # Następnie dodaje wyniki tej metody do kolejki wysyłania
            if self.session:
                messages = self.session.request_to_response()
                if messages:
                    for m in messages:
                        self.sending_queue.put(m)

    # Funkcja dla osobnego wątku do wysyłania
    # przetworzonych wyników

    def sending_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            if not self.sending_queue.empty():
                # Try-catch z powodu problemów z synchronizacją
                try:
                    msg, addr = self.sending_queue.get()
                    self.socket.sendto(msg, addr)
                except:
                    continue

    # Funkcja dla osobnego wątku do odbierania i przetwarzania
    # wiadomości na sesje i żądania

    def recieving_func(self):
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            # W przypadku braku danych w momencie pobierania
            # wyrzucany jest błąd
            try:
                data, addr = self.socket.recvfrom(1024)
            except:
                continue

            if data:
                self.parse_request(repr(data), addr)

    # Przetwarza wiadomość i rozdziela żądania na sesje

    def parse_request(self, message: str, addr: tuple):
        request = Header.parse_message(message)

        # Jeśli komunikat jest niezgodny z protokołem nie obsługujemy go
        if not request.operation == Status.ERROR:
            if request.status == Status.OK:
                print("Client of session {} recieved the message ({})".format(
                    request.id, request.operation))
                return
            # Jeśli klient kończy sesję obsługujemy resztę jego żądań i usuwamy sesje    
            elif request.operation == Operation.DISCONNECTING and self.session.session_id == request.id:
                while not self.session.request_queue.empty():
                    time.sleep(0.1)
                print('Client of session {} is disconnected'.format(request.id))
                self.session = None
                self.sending_queue.put((self.std_server_response(request), addr))
                return

            else:
                print('Recieved from: {}, through port: {}'.format(
                    addr[0], addr[1]))

                # Nowym klientom nadawane jest ID sesji
                if not self.session and request.operation == Operation.CONNECTING and request.id == Status.NONE:
                    request.id = str(randint(0, 99999)).rjust(5, "0")

                # Sprawdzane jest czy klient ma już swoją sesje i jeśli tak dodajemy
                # do niej żądania, jeśli nie to tworzona jest nowa sesja
                if self.session and self.session.session_id == request.id:
                    self.session.request_queue.put(request)
                elif not self.session and not request.id == Status.NONE:
                    new_session = Session(request.id, addr)
                    new_session.request_queue.put(request)
                    self.session = new_session
                else:
                    # Klientom próbującym dołączyć podczas trwania innej sesji odsyłamy błąd
                    print('Another client (id={}) tried to connect, refusing'.format(request.id))
                    self.sending_queue.put((Header.create_reply(request.operation, Status.BUSY, Status.ERROR), addr))
                    return

        # Zwracamy potwierdzenie odbioru komunikatu
        self.sending_queue.put((self.std_server_response(request), addr))

    def std_server_response(self, request: Header) -> bytes:
        return Header.create_reply(request.operation, Status.RECIEVED, request.id, request.a, request.b)


a = Server()
a.run()
