import socket
import struct

def recv_data(sock, timeout=None, st=False):
    if timeout is not None:
        sock.settimeout(timeout)
    start = 0  # just to get rid of that stupid warning

    if st:
        start = time.time()

    lenData = recvall(sock, 4)

    if not lenData:
        return False

    lenData = struct.unpack('>I', lenData)[0]
    data = bytes(recvall(sock, lenData))

    if timeout is not None:
        sock.settimeout(None)

    if st:
        dtime = time.time() - start
        perf = [(lenData + 4) * 8, dtime, 0]
        try:
            speed = (lenData + 4) / dtime / 1024 / 1024 * 8  # speed in Mb/s
            speed = round(speed, 4)

            perf[2] = speed
        except ZeroDivisionError:
            # print("Error, {} bytes recieved in {}ms".format(len(data), dtime/1000))
            pass

        return data, tuple(perf)
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
