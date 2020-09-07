import socket
import struct

def recv_data(sock, timeout=None, st=False):
    if timeout is not None:
        sock.settimeout(timeout)

    lenData = recvall(sock, 4)

    if not lenData:
        return False

    lenData = struct.unpack('>I', lenData)[0]
    data = bytes(recvall(sock, lenData))

    if timeout is not None:
        sock.settimeout(None)

    if st:
        return data, lenData+4  # lenData+4 in bytes
    else:
        return data


def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return False
        data.extend(packet)
    return data
    
    
def addLen(data):
    return struct.pack('>I', len(data)) + data
