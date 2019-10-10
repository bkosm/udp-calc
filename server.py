import socket as skt
import threading as thrdg
from definitions import *


class Server:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind((L_HOST, L_PORT))
        self.numbers_to_sort = []
        self.request_queue = []
        self.stop_recieving = False

    def recieving_func(self):
        while not self.stop_recieving:
            data, addr = self.socket.recvfrom(1024)

            if data:
                print('Recieved from:', addr[0], 'through port:', addr[1])

                message = repr(data)[2:][:-1]

                print("msg =", message)

                self.request_queue.append(message)

                self.socket.sendto(self.std_server_response(Operation.MODULO, 'xd'), addr)

                self.stop_recieving = True


    def run(self):
        self.recieve_requests = thrdg.Thread(target=self.recieving_func)
        
        self.recieve_requests.start()
        self.recieve_requests.join()

        self.socket.close()

        print(self.request_queue)

    def create_reply(self) -> str:

        pass

    def std_server_response(self, operation: str, session_id: str) -> str:
        return Header(operation, Status.RECIEVED, session_id, create_timestamp()).to_send()

a = Server()
a.run()
