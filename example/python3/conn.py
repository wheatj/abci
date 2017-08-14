class ConnReader():

    def __init__(self, conn):
        self.b = bytes()
        self.conn = conn

    def read(self, n):
        while n > len(self.b):
            b = self.conn.recv(1024)
            if not b:
                raise IOError('Dead connection')
            self.b += b
        r = self.b[:n]
        self.b = self.b[n:]
        return r

class ConnWriter():

    def __init__(self, conn):
        self.b = bytes()
        self.conn = conn

    def write(self, b):
        self.b += b

    def flush(self):
        while len(self.b):
            n = self.conn.send(self.b)
            if not n:
                raise IOError('Dead connection')
            self.b = self.b[n:]
