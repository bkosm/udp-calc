from definitions import Operation, Status, Header, Session
import threading as thrdg
from random import randint
from queue import Queue
import socket as skt
import argparse
import time


class Server:
    def __init__(self):
        self.parse_arguments()

        # Inicjalizacja nieblokującego gniazda na UDP
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind((self.arguments.ip_address, self.arguments.port))
        self.socket.setblocking(0)

        # Inicjalizacja bezpiecznych kontenerów
        self.sending_queue = Queue()
        self.counter = [0, 0]
        self.session = None

    def run(self) -> None:
        self.init_threads()

        # Pętla wątku głównego
        cond = ''

        while True:
            cond = input("Type in 'kill' anytime to kill server application\n")
            if cond == 'kill':
                break

        self.stop()

    def stop(self) -> None:
        self.kill_threads()
        self.socket.close()

        print("\nServed {} client(s) with a total of {} operations".format(
            self.counter[1], self.counter[0]))

    def init_threads(self) -> None:
        self.recieve = thrdg.Thread(target=self.recieving_func)
        self.operate = thrdg.Thread(target=self.operation_func)
        self.send = thrdg.Thread(target=self.sending_func)

        self.recieve.daemon = True
        self.operate.daemon = True
        self.send.daemon = True

        self.recieve.start()
        self.operate.start()
        self.send.start()

    def kill_threads(self) -> None:
        self.recieve.run = False
        self.operate.run = False
        self.send.run = False

        self.recieve.join()
        self.operate.join()
        self.send.join()

    # Funkcja dla osobnego wątku do przeprowadzania operacji
    # i kolejkowania ich wyników do wysłania

    def operation_func(self) -> None:
        this_thread = thrdg.currentThread()

        while getattr(this_thread, 'run', True):
            time.sleep(0.1)

            # Wśród wszystkich sesji wykonuje metodę przetwarzania żądania
            # Następnie dodaje wyniki tej metody do kolejki wysyłania
            if self.session:
                messages = self.session.request_to_response()
                if messages:
                    self.counter[0] += 1
                    for m in messages:
                        self.sending_queue.put(m)

    # Funkcja dla osobnego wątku do wysyłania
    # przetworzonych wyników

    def sending_func(self) -> None:
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

    def recieving_func(self) -> None:
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

    def parse_request(self, message: str, addr: tuple) -> None:
        request = Header.parse_message(message)

        # Jeśli komunikat jest niezgodny z protokołem nie obsługujemy go
        if not request.operation == Status.ERROR:
            if request.status == Status.OK:
                print("Client of session {} recieved the message (op={})".format(
                    request.id, request.operation))
                return
            # Jeśli klient kończy sesję obsługujemy resztę jego żądań i usuwamy sesje
            elif request.operation == Operation.DISCONNECTING and self.session and self.session.session_id == request.id:
                while not self.session.request_queue.empty():
                    time.sleep(0.1)

                print('Client of session {} is disconnected'.format(request.id))

                self.session = None
                self.sending_queue.put(
                    (self.std_server_response(request), addr))
                self.counter[1] += 1
                return

            else:
                print('Recieved from: {}, through port: {} (id={})'.format(
                    addr[0], addr[1], request.id))

                # Potwierdzamy odbiór poprawnego komunikatu
                self.sending_queue.put(
                    (self.std_server_response(request), addr))

                # Nowym klientom tworzymy sesję
                if not self.session and request.operation == Operation.CONNECTING and request.id == Status.NONE:
                    request.id = str(randint(0, 99999)).rjust(5, "0")

                    new_session = Session(request.id, addr)
                    new_session.request_queue.put(request)
                    self.session = new_session

                # Żądania od obsługiwanego klienta umieszczcamy do przetworzenia
                elif self.session and self.session.session_id == request.id:
                    self.session.request_queue.put(request)

                # Klientom próbującym dołączyć podczas trwania innej sesji odsyłamy błąd
                else:
                    print(
                        'Another client (id={}) tried to connect, refusing'.format(request.id))
                    self.sending_queue.put((Header.create_reply(
                        status=Status.BUSY, session_id=Status.ERROR), addr))
                    return

        # Odsyłamy informację o niepoprawnym komunikacie
        else:
            self.sending_queue.put((self.std_server_response(request), addr))

    def std_server_response(self, request: Header) -> bytes:
        return Header.create_reply(operation=request.operation, status=Status.RECIEVED, session_id=request.id)

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(
            description="Server of remote calculation application.")

        parser.add_argument(
            "ip_address", help="IP Address to bind to.")
        parser.add_argument(
            "port", type=int, help="Port to listen to.")

        self.arguments = parser.parse_args()


if __name__ == '__main__':
    app = Server()
    app.run()
