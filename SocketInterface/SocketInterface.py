import socket
import threading


def blank_handler(sock, addr):
    # Sample handler
    sock.send(b'Thank you for connecting')
    sock.close()


# Class to define socket connections
class Socket:
    def __init__(self):
        self.sock = socket.socket()

    def bind_port(self, port, max_port):
        while port <= max_port:
            try:
                self.sock.bind(('', port))
                break
            except socket.error:
                port += 1
        else:
            return -1
        return port

    def connect(self, ip, port):
        self.sock.connect((ip, port))

    def send(self, data, data_type='other'):
        if type(data) != type(b''):
            data = data.encode('utf-8')
        return send_pack(self.sock, data, data_type)

    def recv(self):
        return receive_pack(self.sock)

    def listen_loop(self, num, handle_client=blank_handler):
        self.sock.listen(num)
        clients = []
        while True:
            client, addr = self.sock.accept()
            thread = threading.Thread(
                target=handle_client, args=(client, addr, ))
            thread.start()
            clients.append(thread)

    def close(self):
        del self

    def __del__(self):
        self.sock.close()


def send(sock, msg):
    total = 0
    MSGLEN = len(msg)
    while total < MSGLEN:
        sent = sock.send(msg[total:])
        if sent == 0:
            raise RuntimeError("Connection broken")
        total = total + sent
    return total


def receive(sock, MSGLEN):
    chunks = []
    received = 0
    MSGLEN = int(MSGLEN)
    while received < MSGLEN:
        chunk = sock.recv(min(MSGLEN - received, 1024))
        if chunk == b'':
            raise RuntimeError("Connection broken")
        chunks.append(chunk)
        received += len(chunk)
    return b''.join(chunks)


def receive_pack(sock):
    header = receive(sock, 32)
    header = header.decode('utf-8')
    data_type = header[:8]
    length = int(header[8:].strip())
    data = receive(sock, length)
    return data, data_type


def send_pack(sock, data, data_type='other'):
    l = len(data)
    head = create_header(l, data_type)
    head = head.encode('utf-8')
    if send(sock, head) == 32:
        return send(sock, data)
    else:
        return -1


def create_header(length, data_type='other'):
    header = f'{data_type:<8}' + f'{length:<24}'
    return header
