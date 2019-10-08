import socket as skt
from definitions import L_HOST, L_PORT, Header


class Server:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)
        self.socket.bind((L_HOST, L_PORT))
        self.sorting_list = list[int]

    def create_reply(self):
        
        pass

    def __connect__(self):
        data, addr = self.socket.recvfrom(1024)

        print('Connected with: ', addr[0], ' on port:', addr[1])
        print("msg = ", data)

a = Server()
a.__connect__()
