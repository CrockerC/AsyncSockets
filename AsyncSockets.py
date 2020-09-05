import socket
import threading
import util

class multipleListens:
    def __init__(self, socks, perf=False):
        self.socks = socks
        self.perf = perf
        self.listens = dict()
        self.signalRemove = threading.Event()

        self.ret = threading.Semaphore()  # semaphore to protect self.value
        self.got = threading.Event()  # signal for self.loop to yeild the data in self.value
        # self.vSafe = threading.Event()  # signal to self.listen that it is safe to write to self.value
        self.value = []

        self.close = threading.Event()
        self.exception = None

        # self.vSafe.set()

        self.updateListens()

    # loop is meant to be run immediately after the init it called, ie:

    # listen = multipleListens(socks)
    # for data in listen.loop():
    #   handler(data)
    def updateListens(self):
        for sid, sock in enumerate(self.socks):
            if sock not in self.listens:
                self.listens.update({sock: threading.Thread(target=self.listen, args=(sock, sid)).start()})
                # print("added, ", sock)

    def loop(self):
        while True:
            if self.close.isSet():
                if self.exception:
                    if self.exception[1] == 0:
                        raise self.exception
                    else:
                        for sid, sock in enumerate(self.socks):
                            if sid == self.exception[1]:
                                sock.close()
                                self.socks.remove(sock)
                                self.signalRemove.set()
                                break
                return

            self.got.wait()  # wait until we have data for self.value
            self.ret.acquire()  # acquire the semaphore

            yield self.value.pop(0)  # yield the data to the caller
            # self.value = None  # clear the data
            # self.vSafe.set()  # signal that it is now safe to write to self.value again

            if not self.value:
                self.got.clear()  # signal that there is no value in self.value

            self.ret.release()  # release the semaphore

    # todo, handle the loss of a sock
    # todo, any sock other than 0 can be lost without terminating the connection
    def listen(self, sock, sid):
        while True:
            if self.close.isSet():
                return

            if self.perf:
                try:
                    data, speed = recv_data(sock, st=True)  # get data from the socket
                except Exception as ext:
                    self.exception = ext, sid
                    self.close.set()
                    return

                # self.vSafe.wait()  # wait for self.value to be None
                self.ret.acquire()  # acquire the semaphore
                self.value.append((data, speed, sid))  # write the data to self.value
                # self.vSafe.clear()  # signal that it is no longer safe to modify self.value

            else:
                try:
                    data = recv_data(sock)
                except Exception as ext:
                    self.exception = ext
                    self.close.set()
                    return

                # self.vSafe.wait()
                self.ret.acquire()
                self.value.append((data, 0, sid))
                # self.vSafe.clear()

            self.got.set()  # signal that we can now give the value to the caller of self.loop
            self.ret.release()  # release the semaphore

    def close(self):
        self.close.set()
        del self
