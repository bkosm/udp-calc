import socket as skt
from definitions import *


class Server:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind((L_HOST, L_PORT))
        self.lsof_numbers = []

    def run(self):
        while True:
            data, addr = self.socket.recvfrom(1024)

            if data:
                print('Connected with:', addr[0], 'on port:', addr[1])
                print("msg =", repr(data)[1:])

                self.socket.sendto(self.std_server_response(Operation.MODULO, 'xd'), addr)

        self.socket.close()

    def create_reply(self) -> str:

        pass

    def std_server_response(self, operation: str, session_id: str) -> str:
        return Header(operation, Status.RECIEVED, session_id, create_timestamp()).to_send()

a = Server()
a.run()
