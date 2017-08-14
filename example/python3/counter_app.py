from errors import ErrBadNonce, ErrEncodingError
from messages import response_info, response_query
from result import ResultOK
from socket_server import SocketServer

class CounterApplication():

    def __init__(self):
        self.hash_count = 0
        self.serial = False
        self.tx_count = 0

    def info(self):
        resp = response_info()
        resp.info.data = 'hashes:%d, txs:%d' % (self.hash_count, self.tx_count)
        return resp

    def set_option(self, key, value):
        if key == 'serial' and value == 'on':
            self.serial = True
            return 'serial mode on'
        return ''

    def deliver_tx(self, tx_bytes):
        if self.serial:
            if len(tx_bytes) > 8:
                return ErrEncodingError('max tx size is 8 bytes, got %d' % len(tx))
            tx_value = int.from_bytes(tx_bytes, byteorder='big')
            if tx_value != self.tx_count:
                return ErrBadNonce('invalid nonce, expected %d got %d' % (self.tx_count, tx_value))
        self.tx_count += 1
        return ResultOK()

    def check_tx(self, tx_bytes):
        if self.serial:
            if len(tx_bytes) > 8:
                return ErrEncodingError('max tx size is 8 bytes, got %d' % len(tx))
            tx_value = int.from_bytes(tx_bytes, byteorder='big')
            if tx_value < self.tx_count:
                return ErrBadNonce('invalid nonce, expected >= %d got %d' % (self.tx_count, tx_value))
        return ResultOK()

    def commit(self):
        self.hash_count += 1
        if self.tx_count == 0:
            return ResultOK()
        h = self.tx_count.to_bytes(8, byteorder='big')
        return ResultOK(h, '')

    def query(self, query):
        resp = response_query()
        if query.path == 'hash':
            resp.query.value = bytes(str(self.hash_count).encode())
        elif query.path == 'tx':
            resp.query.value = bytes(str(self.tx_count).encode())
        else:
            resp.query.log = 'invalid query path, expected "hash" or "tx", got "%s"' % query.path
        return resp

if __name__ == '__main__':

    print('ABCI Counter App (Python3)')

    app = CounterApplication()
    server = SocketServer('127.0.0.1:46658', app)
    server.on_start()
