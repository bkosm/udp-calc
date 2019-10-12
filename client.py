import socket as skt
from definitions import *


class Client:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.HOST = L_HOST
        self.PORT = L_PORT

    def run(self):
        self.socket.sendto(self.connection_request(), (self.HOST, self.PORT))

        data, addr = self.socket.recvfrom(1024)

        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

        data, addr = self.socket.recvfrom(1024)

        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

        sess_id = Header.parse_message(repr(data)).id

        print('New list')
        self.socket.sendto(Header.create_reply(
            Operation.SORT_A, Status.SENDING, sess_id, '3', '0'), (self.HOST, self.PORT))

        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

        self.socket.sendto(Header.create_reply(
            Operation.SORT_D, Status.LAST, sess_id, '20', '0'), (self.HOST, self.PORT))

        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

        print('New list')
        self.socket.sendto(Header.create_reply(
            Operation.SORT_A, Status.SENDING, sess_id, '10', '0'), (self.HOST, self.PORT))

        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

        self.socket.sendto(Header.create_reply(
            Operation.SORT_A, Status.LAST, sess_id, '-1', '0'), (self.HOST, self.PORT))

        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])
        data, addr = self.socket.recvfrom(1024)
        print('Connected with:', addr[0], 'on port:', addr[1])
        print("msg =", repr(data)[1:])

    def connection_request(self):
        return Header.create_reply(Operation.CONNECTING, Status.CONNECTING, Status.NONE)

    def std_client_response(self, operation: str, session_id: str) -> str:
        return Header.create_reply(operation, Status.OK, session_id)


a = Client()
a.run()
