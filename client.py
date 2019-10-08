import socket as skt
from definitions import L_HOST, L_PORT


class Client:
    def __init__(self):
        self.socket = skt.socket(skt.AF_INET, skt.SOCK_DGRAM)

    def send(self):
        self.socket.sendto(bytes('Siema', encoding='utf8'), (L_HOST, L_PORT))

a = Client()
a.send()